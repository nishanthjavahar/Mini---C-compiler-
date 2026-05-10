from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class ASTNode:
    kind: str
    children: List[Any] = field(default_factory=list)
    value: Any = None
    line: int = 0