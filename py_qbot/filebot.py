import shutil
import subprocess
import sys
from typing import Literal, Optional

from py_qbot import logger


class FileBot:
    def __init__(self) -> None:
        self.executable = self._find_filebot()
        self._ensure_filebot(self.executable)

    def rename(
        self,
        path: str,
        output: str,
        format: Optional[str] = None,
        filter: Optional[str] = None,
        manual_query: Optional[str] = None,
        db: Optional[
            Literal["TheMovieDB::TV", "TheTVDB", "AniDB", "TheMovieDB", "OMDb", "AcoustID", "ID3"]
        ] = None,
        action: Optional[Literal["move", "copy", "hardlink", "symlink", "test"]] = None,
        conflict: Optional[Literal["skip", "replace", "auto", "index", "fail"]] = None,
        non_strict: bool = False,
    ):
        """Renames a file using FileBot.

        Args:
            path (str): The input directory that contains the files to rename.
            output (str): The output directory where the renamed files will be saved.
            format (Optional[str]): The format string to use for the new file name.
            filter (Optional[str]): The filter to apply to the file.
            manual_query (Optional[str]): The manual query to use for the file.
            db (Optional[Literal["TheMovieDB::TV", "TheTVDB", "AniDB", "TheMovieDB", "OMDb", "AcoustID", "ID3"]]): The database to use for the file.
            action (Optional[Literal["move", "copy", "hardlink", "symlink", "test"]]): The action to perform on the file.
            conflict (Optional[Literal["skip", "replace", "auto", "index", "fail"]]): The conflict resolution strategy to use.
            non_strict (bool, optional): Whether to use non-strict matching. Defaults to False.
        """
        if not self.executable:
            logger.error("FileBot executable not found. Please install it or add it to PATH.")
            sys.exit(1)

        # mandatory arguments
        cmd = [
            self.executable,
            "-rename",
            path,
            "--output",
            output,
            "-r",  # recursive
        ]

        # optional arguments
        if format:
            cmd.extend(["--format", format])
        if filter:
            cmd.extend(["--filter", filter])
        if manual_query:
            cmd.extend(["--q", manual_query])
        if db:
            cmd.extend(["--db", db])
        if action:
            cmd.extend(["--action", action])
        if conflict:
            cmd.extend(["--conflict", conflict])
        if non_strict:
            cmd.extend(["-non-strict"])

        # print the command for debugging
        if sys.platform.startswith("win"):
            cmd_str = subprocess.list2cmdline(cmd)
        else:
            import shlex

            cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
        logger.info(f"Running FileBot command: {cmd_str}")

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("FileBot successfully executed.")
        except subprocess.CalledProcessError as e:
            # e.stdout / e.stderr are the captured output
            logger.error(f"FileBot command failed (exit {e.returncode})")
            if e.stdout:
                logger.error("\n=== stdout ===\n%s", e.stdout.rstrip())
            if e.stderr:
                logger.error("\n=== stderr ===\n%s", e.stderr.rstrip())

            raise RuntimeError(
                f"FileBot command failed with exit code {e.returncode}. "
                "Check the logs for more details."
            ) from e

    @staticmethod
    def _find_filebot() -> str | None:
        """
        Returns the absolute path to the 'filebot' executable if it is on the PATH,
        or None if not found.
        """
        return shutil.which("filebot")

    @staticmethod
    def _verify_filebot(path: str) -> bool:
        """
        Runs 'filebot --version' to confirm that the executable at `path` is
        really FileBot and is functional.
        """
        try:
            result = subprocess.run(
                [path, "-version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            # should never happen if shutil.which passed back a path
            return False
        except subprocess.CalledProcessError:
            # filebot exists but returned an error code
            return False

        # Optionally inspect result.stdout for more confidence:
        return "FileBot" in result.stdout

    @staticmethod
    def _ensure_filebot(fb):
        if not fb:
            logger.error(
                f"FileBot executable not found in PATH. Please install it or add it to PATH: {fb}"
            )
            sys.exit(1)
        if not FileBot._verify_filebot(fb):
            logger.error(f"FileBot executable at {fb} is not valid or not working.")
            sys.exit(1)
        logger.debug(f"FileBot is installed and working at: {fb}")

    def version(self) -> str:
        version = subprocess.run(
            ["filebot", "-version"], capture_output=True, text=True, check=True
        )
        # remove "Filebot " prefix from the output
        if not version.stdout.startswith("FileBot "):
            raise ValueError("Unexpected output from filebot -version command")
        return version.stdout.replace("FileBot ", "").strip()
