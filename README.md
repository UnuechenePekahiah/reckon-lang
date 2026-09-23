# Reckon

A small, Turing-incomplete calculator language with variables, string
output, and a single-branch `if`/`else` — built from scratch in Python
for **CSC 404: Survey of Programming Languages** (Niger Delta University).

No parser-generator libraries (ANTLR, YACC, etc.) are used anywhere in this
project — the lexer, parser, and evaluator are all hand-written.

## Status

- [x] **Week 1** — Language spec + lexer (`spec.md`, `lexer.py`)
- [ ] **Week 2** — Recursive-descent parser / AST (`parser.py`)
- [ ] **Week 3** — Evaluator + test script (`evaluator.py`, `main.py`, `*.reckon`)

## Example

```
let score = 75
if score >= 50 {
    show "Pass"
} else {
    show "Fail"
}
```

See [`spec.md`](spec.md) for the full lexical and syntactic grammar, plus
more example programs.

## Project structure

```
.
├── spec.md        # Language specification (EBNF grammar + examples)
├── lexer.py        # Week 1: hand-written tokenizer
├── parser.py        # Week 2: recursive-descent parser (coming)
├── evaluator.py      # Week 3: tree-walking interpreter (coming)
├── main.py         # Week 3: entry point (coming)
└── .gitignore
```

## Running the lexer

The lexer has a small self-test/demo built in — it tokenizes five sample
programs from `spec.md` and then demonstrates graceful error handling on
an illegal character and an unterminated string:

```bash
python lexer.py
```

To use it in your own code:

```python
from lexer import tokenize

for token in tokenize('let x = 5 + 3'):
    print(token)
```

## Author

Unuechene Peremobowei Pekahiah — Ug/22/5905
