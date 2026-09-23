# Reckon — Language Specification

## 1. Overview

**Reckon** is a small, Turing-incomplete language for doing arithmetic with
named variables, printing results, and branching once on a condition. It has
no loops, no user-defined functions, and no recursion, so every program is
guaranteed to halt.

## 2. Example Programs

**2.1 — Variables and arithmetic**
```
let a = 10
let b = 3
let c = a + b * 2
show c
```

**2.2 — Operator precedence and parentheses**
```
let result = (5 + 3) * 2 - 4 / 2
show result
```

**2.3 — String output**
```
show "Starting calculation..."
let x = 42
show x
```

**2.4 — Conditional block (if / else, no loops)**
```
let score = 75
if score >= 50 {
    show "Pass"
} else {
    show "Fail"
}
```

**2.5 — Comments**
```
# Computes the area of a rectangle
let width = 4
let height = 7
let area = width * height
show area
```

## 3. Lexical Grammar (tokens)

```
DIGIT       = "0".."9"
LETTER      = "a".."z" | "A".."Z" | "_"

INTEGER     = DIGIT , { DIGIT } ;
FLOAT       = DIGIT , { DIGIT } , "." , DIGIT , { DIGIT } ;
IDENTIFIER  = LETTER , { LETTER | DIGIT } ;
STRING      = '"' , { any character except '"' } , '"' ;

KEYWORD     = "let" | "show" | "if" | "else" | "true" | "false" ;

OPERATOR    = "+" | "-" | "*" | "/" | "%"
            | "=" | "==" | "!="
            | "<" | ">" | "<=" | ">=" ;

DELIMITER   = "(" | ")" | "{" | "}" ;

COMMENT     = "#" , { any character except newline } ;   (* discarded by the lexer *)
```

## 4. Syntactic Grammar (EBNF) — target for Weeks 2–3

```
program      = { statement } ;

statement    = let_stmt | show_stmt | if_stmt ;

let_stmt     = "let" , identifier , "=" , expression ;

show_stmt    = "show" , expression ;

if_stmt      = "if" , expression , "{" , { statement } , "}" ,
               [ "else" , "{" , { statement } , "}" ] ;

expression   = comparison ;

comparison   = term , [ ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) , term ] ;

term         = factor , { ( "+" | "-" ) , factor } ;

factor       = unary , { ( "*" | "/" | "%" ) , unary } ;

unary        = [ "-" ] , primary ;

primary      = INTEGER | FLOAT | STRING | "true" | "false"
             | identifier
             | "(" , expression , ")" ;
```

Precedence, low to high: comparison → addition/subtraction → multiplication/
division/modulo → unary minus → primary. This matches the nesting order of
the grammar above (each rule calls the next-tighter-binding rule).

## 5. Why Reckon is Turing-incomplete

- No loops (`for` / `while`) — nothing can repeat.
- No user-defined functions and no recursion.
- `if` / `else` bodies can contain further statements (including nested
  `if`s), but there is no construct that repeats execution, so every
  program has a fixed, finite number of steps and always halts.

## 6. Deliverables mapping

| Week | File | Status |
|------|------|--------|
| 1 | `spec.md` | this document |
| 1 | `lexer.py` | tokenizer implementing Section 3 |
| 2 | `parser.py` | recursive-descent parser implementing Section 4 |
| 3 | `evaluator.py`, `main.py`, `*.reckon` test script | tree-walking interpreter |
