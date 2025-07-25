from typing import List, Optional

from py_qbot import logger


class ExtraArgument:
    def __init__(self, extra: str = "", key_value_delimiter: str = ":") -> None:
        self.filter: Optional[str] = None
        self.excludes: List[str] = []
        self.name: Optional[str] = None
        self.is_direct: bool = False
        self._extra_raw = extra
        self._key_value_delimiter = key_value_delimiter
        self.parse()

    def _parse_dict(self) -> dict[str, str]:
        if not self._extra_raw:
            return {}

        result = {}
        for item in self._extra_raw.split(","):
            if not item.strip():
                continue  # skip empty items
            if self._key_value_delimiter not in item:
                logger.warning(
                    f"Ignoring invalid argument: '{item}' (missing '{self._key_value_delimiter}')"
                )
                continue
            key, value = item.split(self._key_value_delimiter, 1)  # only split on the first ':'
            key = key.strip()
            value = value.strip()
            if not key:
                logger.warning(f"Ignoring argument with empty key: '{item}'")
                continue
            result[key.upper()] = value  # normalize key to uppercase
        return result

    def parse(self) -> None:
        parsed = self._parse_dict()
        self.filter = parsed.get("FILTER")
        self.excludes = parsed.get("EXCLUDES", "").split(";") if parsed.get("EXCLUDES") else []
        self.name = parsed.get("NAME")
        self.is_direct = parsed.get("DIRECT", "false").lower() == "true"
