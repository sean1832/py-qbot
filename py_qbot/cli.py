import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from py_qbot import __version__, logger
from py_qbot.config import QBotConfig
from py_qbot.qbot import QBot


def parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"PY-QBot CLI ({__version__})")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration file",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input directory containing media files to rename",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="Name for the media files",
    )
    parser.add_argument(
        "-c",
        "--category",
        type=str,
        choices=["anime", "tv", "movie"],
        required=True,
        help="Category of the media files",
    )
    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        help="(Optional) File filter for selecting specific media files",
    )
    parser.add_argument(
        "--fuzzy",
        action="store_true",
        default=False,
        help="(Optional) Enable fuzzy matching for media names",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="(Optional) Enable debug logging",
    )
    parser.add_argument(
        "--extra",
        type=str,
        help="(Optional) Extra arguments to pass to the script. semi-colon-separated key:value pairs. supported keys: 'FILTER', 'EXCLUDE'",
    )
    parser.add_argument(
        "--log",
        type=str,
        help="(Optional) Path to the log file",
    )

    return parser.parse_args()


def configure_logging(dir: Path, debug: bool) -> None:
    # Ensure your log directory exists
    dir.mkdir(parents=True, exist_ok=True)

    # Compute today’s filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_path = dir / f"{date_str}.log"

    # Pick your level
    level = logging.DEBUG if debug else logging.INFO

    # Create handlers
    handlers = []  #  type is list[Any], so you can mix handlers
    handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    handlers.append(logging.StreamHandler())

    # Apply configuration
    logging.basicConfig(
        level=level,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def parse_extra_args(extra: str, key_value_delimiter: str = ":") -> dict[str, str]:
    if not extra:
        return {}

    result = {}
    for item in extra.split(";"):
        if not item.strip():
            continue  # skip empty items
        if key_value_delimiter not in item:
            logger.warning(f"Ignoring invalid argument: '{item}' (missing '{key_value_delimiter}')")
            continue
        key, value = item.split(key_value_delimiter, 1)  # only split on the first ':'
        key = key.strip()
        value = value.strip()
        if not key:
            logger.warning(f"Ignoring argument with empty key: '{item}'")
            continue
        result[key.upper()] = value  # normalize key to uppercase
    return result


def main():
    args = parser()
    log_raw = args.log or "~/py-qbot/logs"
    log_dir = Path(log_raw).expanduser().resolve()

    # Configure logging
    configure_logging(log_dir, args.debug)

    # parse configuration file
    if not args.config.endswith(".json"):
        logger.error("Configuration file must be a JSON file. Please provide a valid path.")
        return
    with open(Path(args.config).expanduser().resolve(), "r") as f:
        try:
            config_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading configuration file: {e}")
            return
    config = QBotConfig(config_data)

    # parse extra arguments
    extra_args = parse_extra_args(args.extra)
    filter = extra_args.get("FILTER", args.filter)
    exclude_dir_str = extra_args.get("EXCLUDE", None)
    if exclude_dir_str:
        # Convert the exclude directories to a list
        exclude_dirs = [d.strip() for d in exclude_dir_str.split("|") if d.strip()]
        config.categories[args.category].exclude_dirs.extend(exclude_dirs)
        logger.debug(f"Added extra exclude directories: {exclude_dirs}")

    with QBot(config) as qbot:
        # Ensure input path is absolute
        args.input = Path(args.input).expanduser().resolve()
        if not args.input.exists() or not args.input.is_dir():
            print(f"Input directory '{args.input}' does not exist or is not a directory.")
            return

        # Perform renaming operation
        qbot.rename(
            input_root=Path(args.input).resolve(),
            media_name=args.name,
            category=args.category,
            filter=filter,
            is_fuzzy=args.fuzzy,
        )


if __name__ == "__main__":
    main()
