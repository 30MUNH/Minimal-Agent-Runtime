from __future__ import annotations

from pathlib import Path


SEED_FILES = {
    "app.py": """def main():
    # TODO: validate command line arguments
    print("hello")
""",
    "notes.md": """# Project Notes

TODO: write reviewer setup instructions
TODO: document the memory file location
""",
    "src/helpers.py": """def normalize(value):
    # TODO: handle empty strings
    return value.strip().lower()
""",
    "tests/sample.txt": """This file has no action item.
""",
}


def seed_workspace(workspace: str | Path = "workspace") -> Path:
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)
    for relative_path, content in SEED_FILES.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def main() -> None:
    root = seed_workspace()
    print(f"Seeded {root} with {len(SEED_FILES)} files.")


if __name__ == "__main__":
    main()
