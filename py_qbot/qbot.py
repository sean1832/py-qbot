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
    ):
        exclude_dirs = self.config.categories[category].exclude_dirs
        match_patterns = self.config.categories[category].match_patterns

        files = self._list_files(input_root, exclude_dirs, match_patterns)
        if not files or len(files) <= 0:
            logger.warning(f"No source files found for {media_name}")
            return

        # move to temporary directory
        if not self.config.temp_dir.exists():
            self.config.temp_dir.mkdir(parents=True, exist_ok=True)
        files = self._move_files(files, input_root, self.config.temp_dir / media_name)

        # compute output path
        output = self.config.categories[category].path  # e.g. /mnt/nas/Media/animes
        if not output:
            logger.error(f"Invalid category '{category}' for media '{media_name}'")
            return
        output = Path(output).resolve()  # resolve to absolute path

        # db
        db = self.config.categories[category].db

        # format
        format = self.config.categories[category].format
        # run filebot
        self.filebot.rename(
            path=str(self.config.temp_dir / media_name),
            output=str(output),
            filter=filter,
            db=db,
            manual_query=media_name,
            conflict="skip",
            action="move",
            format=format,
            non_strict=is_fuzzy,
        )
        self._cleanup_directory(self.config.temp_dir / media_name)

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
