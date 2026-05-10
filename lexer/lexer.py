from lexer.tokens import *

def tokenize(source: str):

    tokens = []
    errors = []

    line = 1

    for mo in TOKEN_RE.finditer(source):

        kind = mo.lastgroup
        val = mo.group()

        if kind == 'NEWLINE':
            line += 1

        elif kind in ('SKIP', 'COMMENT', 'MCOMMENT'):
            line += val.count('\n')

        elif kind == 'MISMATCH':
            errors.append(
                f"[Lexer] Line {line}: Unexpected character '{val}'"
            )

        else:

            if kind == 'ID' and val in KEYWORDS:
                kind = val.upper()

            tokens.append(Token(kind, val, line))

    return tokens, errors