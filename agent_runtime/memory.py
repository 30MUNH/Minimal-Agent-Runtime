from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonMemory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._data = self._load()

    def remember(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8")

    def recall(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def context(self) -> dict[str, Any]:
        return dict(self._data)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
