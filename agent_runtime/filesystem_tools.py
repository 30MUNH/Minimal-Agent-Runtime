from __future__ import annotations

from pathlib import Path

from .tools import Tool


def build_filesystem_tools(workspace: str | Path) -> list[Tool]:
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return [
        Tool(
            "list_files",
            "List files in the workspace.",
            {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
                "additionalProperties": False,
            },
            lambda args: _list_files(root, str(args.get("path", "."))),
        ),
        Tool(
            "read_file",
            "Read a UTF-8 text file from the workspace.",
            {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
            lambda args: _read_file(root, str(args["path"])),
        ),
        Tool(
            "write_file",
            "Write a UTF-8 text file inside the workspace.",
            {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            lambda args: _write_file(root, str(args["path"]), str(args["content"])),
        ),
        Tool(
            "search_files",
            "Search workspace text files for a query string.",
            {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
            lambda args: _search_files(root, str(args["query"])),
        ),
    ]


def _resolve(root: Path, user_path: str) -> Path:
    path = (root / user_path).resolve()
    if root != path and root not in path.parents:
        raise ValueError(f"path is outside workspace: {user_path}")
    return path


def _list_files(root: Path, path: str) -> list[str]:
    base = _resolve(root, path)
    if not base.exists():
        return []
    files = [item.relative_to(root).as_posix() for item in base.rglob("*") if item.is_file()]
    return sorted(files)


def _read_file(root: Path, path: str) -> str:
    return _resolve(root, path).read_text(encoding="utf-8")


def _write_file(root: Path, path: str, content: str) -> str:
    target = _resolve(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target.relative_to(root).as_posix()


def _search_files(root: Path, query: str) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for path in _list_files(root, "."):
        full_path = _resolve(root, path)
        try:
            lines = full_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if query in line:
                matches.append({"path": path, "line": index, "text": line.strip()})
    return matches
