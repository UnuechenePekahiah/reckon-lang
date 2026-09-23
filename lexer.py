"""
lexer.py — Tokenizer for the Reckon language.

Reckon is a small Turing-incomplete calculator language with variables,
string output, and a single-branch if/else. See spec.md for the full
lexical and syntactic grammar.

This lexer is written entirely from scratch (no regex-based tokenizer
generators, no parser-generator libraries) as required by the BYOL
project rules.
"""

from enum import Enum, auto


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    LET = auto()
    SHOW = auto()
    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()       # =
    EQ = auto()           # ==
    NEQ = auto()          # !=
    LT = auto()           # <
    GT = auto()           # >
    LTE = auto()          # <=
    GTE = auto()          # >=

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()

    # Housekeeping
    EOF = auto()


KEYWORDS = {
    "let": TokenType.LET,
    "show": TokenType.SHOW,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

# Multi-character operators must be checked before their single-character
# prefixes (e.g. "==" before "=").
TWO_CHAR_OPERATORS = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
}

ONE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "=": TokenType.ASSIGN,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
}


class Token:
    __slots__ = ("type", "value", "line", "col")

    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"

    def __eq__(self, other):
        # Convenience for tests: compare by (type, value) only.
        if isinstance(other, tuple):
            return (self.type, self.value) == other
        return NotImplemented


class LexError(Exception):
    """Raised on an illegal character or a malformed literal."""

    def __init__(self, message, line, col):
        super().__init__(f"Lex error at {line}:{col} — {message}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    # ---- low-level cursor helpers -------------------------------------

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return ""

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _at_end(self):
        return self.pos >= len(self.source)

    # ---- skipping ------------------------------------------------------

    def _skip_whitespace_and_comments(self):
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "#":
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            else:
                break

    # ---- literal scanners -----------------------------------------------

    def _scan_number(self):
        start_line, start_col = self.line, self.col
        start = self.pos
        is_float = False

        while not self._at_end() and self._peek().isdigit():
            self._advance()

        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()  # consume '.'
            while not self._at_end() and self._peek().isdigit():
                self._advance()

        text = self.source[start:self.pos]
        if is_float:
            return Token(TokenType.FLOAT, float(text), start_line, start_col)
        return Token(TokenType.INTEGER, int(text), start_line, start_col)

    def _scan_identifier_or_keyword(self):
        start_line, start_col = self.line, self.col
        start = self.pos
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        text = self.source[start:self.pos]
        keyword_type = KEYWORDS.get(text)
        if keyword_type is not None:
            return Token(keyword_type, text, start_line, start_col)
        return Token(TokenType.IDENTIFIER, text, start_line, start_col)

    def _scan_string(self):
        start_line, start_col = self.line, self.col
        self._advance()  # consume opening quote
        chars = []
        while True:
            if self._at_end():
                raise LexError("unterminated string literal", start_line, start_col)
            ch = self._peek()
            if ch == '"':
                self._advance()  # consume closing quote
                break
            if ch == "\n":
                raise LexError("unterminated string literal (newline before closing \")",
                                start_line, start_col)
            if ch == "\\":
                self._advance()
                escaped = self._peek()
                escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                if escaped in escapes:
                    chars.append(escapes[escaped])
                    self._advance()
                else:
                    raise LexError(f"unknown escape sequence '\\{escaped}'",
                                   self.line, self.col)
            else:
                chars.append(ch)
                self._advance()
        return Token(TokenType.STRING, "".join(chars), start_line, start_col)

    # ---- main driver -----------------------------------------------------

    def tokenize(self):
        tokens = []
        while True:
            self._skip_whitespace_and_comments()
            if self._at_end():
                tokens.append(Token(TokenType.EOF, None, self.line, self.col))
                break

            ch = self._peek()
            line, col = self.line, self.col

            if ch.isdigit():
                tokens.append(self._scan_number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self._scan_identifier_or_keyword())
                continue

            if ch == '"':
                tokens.append(self._scan_string())
                continue

            two = self._peek() + self._peek(1)
            if two in TWO_CHAR_OPERATORS:
                self._advance()
                self._advance()
                tokens.append(Token(TWO_CHAR_OPERATORS[two], two, line, col))
                continue

            if ch in ONE_CHAR_TOKENS:
                self._advance()
                tokens.append(Token(ONE_CHAR_TOKENS[ch], ch, line, col))
                continue

            # Illegal character: report it and skip past it so the lexer
            # can keep going and surface further errors in one pass,
            # rather than crashing on the first bad character.
            raise LexError(f"illegal character {ch!r}", line, col)

        return tokens


def tokenize(source: str):
    """Convenience wrapper: tokenize a source string, return a list of Tokens."""
    return Lexer(source).tokenize()


# ---- self-test / demo ----------------------------------------------------

if __name__ == "__main__":
    samples = [
        '''let a = 10
let b = 3
let c = a + b * 2
show c''',
        '''let result = (5 + 3) * 2 - 4 / 2
show result''',
        '''show "Starting calculation..."
let x = 42
show x''',
        '''let score = 75
if score >= 50 {
    show "Pass"
} else {
    show "Fail"
}''',
        '''# Computes the area of a rectangle
let width = 4
let height = 7
let area = width * height
show area''',
    ]

    for i, src in enumerate(samples, start=1):
        print(f"--- sample {i} ---")
        print(src)
        print("tokens:")
        for tok in tokenize(src):
            if tok.type != TokenType.EOF:
                print(" ", tok)
        print()

    # Error-handling demo: illegal character and unterminated string
    for bad_src in ["let x = 5 @ 2", 'show "unterminated']:
        print(f"--- expected error for: {bad_src!r} ---")
        try:
            tokenize(bad_src)
        except LexError as e:
            print(" ", e)
        print()
