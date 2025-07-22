import fnmatch
import os
import shutil
from pathlib import Path
from typing import List, Literal, Optional

from py_qbot import logger
from py_qbot.config import QBotConfig
from py_qbot.filebot import FileBot


class QBot:
    def __init__(self, config: QBotConfig) -> None:
        self.filebot = FileBot()
        self.config = config

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit point."""
        # # Cleanup temporary directory if it exists and not containing any files
        # if self.config.temp_dir.exists():
        #     self._cleanup_directory(self.config.temp_dir)
        #     logger.debug(f"QBot context exited and {self.config.temp_dir} directory cleaned up.")

    def rename(
        self,
        media_name: str,
        input_root: Path,
        category: Literal["anime", "tv", "movie"],
        filter: Optional[str] = None,
        is_fuzzy: bool = False,
        use_temp: bool = True,
    ):
        # Gather config
        media_type = self.config.categories.get(category)
        if not media_type:
            logger.error(f"Invalid category '{category}'")
            return

        exclude_dirs: List[str] = media_type.exclude_dirs
        match_patterns: List[str] = media_type.match_patterns
        output_root: Path = Path(media_type.path).resolve()
        db, format = media_type.db, media_type.format

        # List & early exit
        files = self._list_files(input_root, exclude_dirs, match_patterns)
        if not files:
            logger.warning(f"No source files found for '{media_name}'")
            return

        # Optionally stage files in temp_dir
        work_path = input_root
        if use_temp:
            temp_target = self.config.temp_dir / media_name
            temp_target.mkdir(parents=True, exist_ok=True)
            files = self._move_files(files, input_root, temp_target)
            work_path = temp_target

        # Call FileBot
        try:
            self.filebot.rename(
                path=str(work_path),
                output=str(output_root),
                filter=filter,
                db=db,
                manual_query=media_name,
                conflict="replace",
                action="move",
                format=format,
                non_strict=is_fuzzy,
            )
            # Cleanup
            cleanup_target = work_path if use_temp else input_root
            self._cleanup_directory(cleanup_target)
        except Exception as exc:
            logger.error(
                f"Error renaming '{media_name}' "
                f"({'temp' if use_temp else 'direct'}) -> {exc}"
            )

    def _move_files(self, files: List[Path], input_root: Path, output_root: Path):
        result_files = []
        input_root = input_root.resolve()
        for src in files:
            # compute path relative to your input root
            rel = src.resolve().relative_to(input_root)
            # this is where it should land under temp_dir/media_name/...
            dest = output_root / rel

            # make sure parent folders exist
            dest.parent.mkdir(parents=True, exist_ok=True)
            # move the file
            shutil.move(str(src), str(dest))
            logger.debug(f"MOVED ({src}) -> ({dest})")

            result_files.append(dest)

        return result_files

    def _cleanup_directory(self, path: Path):
        """Remove all files and directories in the specified path."""
        if not path.exists():
            return

        for item in path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        # Remove the directory itself if it's empty
        if not any(path.iterdir()):
            path.rmdir()
        logger.debug(f"Cleaned up directory: {path}")

    def _list_files(
        self, path: Path, exclude_dirs: List[str], match_patterns: List[str]
    ) -> List[Path]:
        all_files = []

        # normalize patterns to lowercase for case‑insensitive matching
        patterns = [pat.lower() for pat in match_patterns]
        logger.debug(
            f"Listing files in {path} with patterns: {patterns} and excluding dirs: {exclude_dirs}"
        )

        for root, dirs, files in os.walk(path):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in files:
                name_lower = filename.lower()
                if patterns and not any(fnmatch.fnmatch(name_lower, pat) for pat in patterns):
                    continue
                all_files.append(Path(root) / filename)
        return all_files
