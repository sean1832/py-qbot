from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal

# define types
Category = Literal["anime", "tv", "movie"]
MediaDatabase = Literal[
    "TheMovieDB::TV", "TheTVDB", "AniDB", "TheMovieDB", "OMDb", "AcoustID", "ID3"
]


@dataclass
class QBotDefaults:
    exclude_dirs: List[str] = field(default_factory=list)
    match_patterns: List[str] = field(
        default_factory=lambda: ["*.mkv", "*.mp4", "*.avi", "*.mov", "*.rmvb", "*.webm"]
    )


@dataclass
class CategoryConfig:
    path: Path
    format: str
    db: MediaDatabase
    exclude_dirs: List[str] = field(default_factory=list)
    match_patterns: List[str] = field(default_factory=list)


class QBotConfig:
    def __init__(self, cfg: dict) -> None:
        # Temp dir
        self.temp_dir = Path(cfg["temp_dir"]).resolve()
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Global defaults
        defaults_block = cfg.get("defaults", {})
        self.defaults = QBotDefaults(
            exclude_dirs=defaults_block.get("exclude_dirs", []),
            match_patterns=defaults_block.get("match_patterns", []),
        )

        # Per‑category raw
        self.categories: Dict[Category, CategoryConfig] = {
            name: CategoryConfig(
                path=Path(cat["path"]).resolve(),
                format=cat["format"],
                db=cat["db"],
                exclude_dirs=cat.get("exclude_dirs"),
                match_patterns=cat.get("match_patterns"),
            )
            for name, cat in cfg.get("categories", {}).items()
        }

        # Inject defaults into any None fields
        for cat in self.categories.values():
            if cat.exclude_dirs is None:
                cat.exclude_dirs = list(self.defaults.exclude_dirs)
            if cat.match_patterns is None:
                cat.match_patterns = list(self.defaults.match_patterns)
