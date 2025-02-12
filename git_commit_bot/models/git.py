from dataclasses import dataclass

@dataclass
class DiffInfo:
    files_changed: list[str]
    diff_content: str