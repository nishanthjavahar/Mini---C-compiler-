from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Symbol:
    name: str
    type: str
    scope: str
    is_array: bool = False
    array_size: Optional[int] = None
    initialized: bool = False


class SymbolTable:

    def __init__(self):

        self.scopes: List[Dict[str, Symbol]] = [{}]

        self.all_symbols: List[Symbol] = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def current_scope_name(self):
        return f"scope_{len(self.scopes)-1}"

    def declare(self, sym: Symbol):

        top = self.scopes[-1]

        if sym.name in top:
            return False

        sym.scope = self.current_scope_name()

        top[sym.name] = sym

        self.all_symbols.append(sym)

        return True

    def lookup(self, name):

        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None

    def to_table(self):

        rows = []

        for s in self.all_symbols:

            t = f"{s.type}[{s.array_size}]" if s.is_array else s.type

            rows.append({
                'name': s.name,
                'type': t,
                'scope': s.scope,
                'initialized': s.initialized
            })

        return rows