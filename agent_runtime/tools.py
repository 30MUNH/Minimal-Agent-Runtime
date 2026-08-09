from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]

    def run(self, args: dict[str, Any]) -> Any:
        if not isinstance(args, Mapping):
            raise TypeError("tool arguments must be a mapping")
        return self.handler(dict(args))
