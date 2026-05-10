import re
from dataclasses import dataclass

KEYWORDS = {
    'int', 'float', 'if', 'else',
    'while', 'for', 'print',
    'return', 'void'
}

TOKEN_SPEC = [
    ('FLOAT_LIT',  r'\d+\.\d+'),
    ('INT_LIT',    r'\d+'),
    ('STRING_LIT', r'"[^"]*"'),
    ('ID',         r'[A-Za-z_]\w*'),

    ('LBRACKET',   r'\['),
    ('RBRACKET',   r'\]'),

    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),

    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),

    ('SEMICOLON',  r';'),
    ('COMMA',      r','),

    ('LE',         r'<='),
    ('GE',         r'>='),
    ('EQ',         r'=='),
    ('NE',         r'!='),

    ('LT',         r'<'),
    ('GT',         r'>'),

    ('ASSIGN',     r'='),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('STAR',       r'\*'),
    ('SLASH',      r'/'),

    ('NEWLINE',    r'\n'),
    ('SKIP',       r'[ \t\r]+'),

    ('COMMENT',    r'//[^\n]*'),
    ('MCOMMENT',   r'/\*.*?\*/'),

    ('MISMATCH',   r'.'),
]

TOKEN_RE = re.compile(
    '|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPEC),
    re.DOTALL
)

@dataclass
class Token:
    type: str
    value: str
    line: int