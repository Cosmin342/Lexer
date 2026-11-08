# Lexer

Python tools for DFA-based lexing, regular-expression conversion, and parsing a small imperative language.

## Python Modules

### `Lexer.py`

Runs token rules supplied as DFA transition tables. At each position, it chooses the token with the longest accepted prefix, or reports the error location. `runlexer(in_lex, in_data, out)` reads the specification and input, then writes token-lexeme pairs.

### `RegexConverter.py`

Converts prefix-form expressions (`CONCAT`, `UNION`, `STAR`, `PLUS`, and literals) to DFAs. It builds an NFA, applies epsilon-closure subset construction, and adds a sink state for missing transitions. Run it with an input expression and output path:

```text
python3 RegexConverter.py <regex-input> <dfa-output>
```

### `CompleteLexer.py`

Builds automata from regex-based token rules and uses longest-prefix tokenization. It also parses imperative programs with instruction lists, assignments, expressions, conditionals, and loops into AST nodes from `ast_utils.py`. Entry points: `runcompletelexer(in_lex, in_data, out)` and `runparser(inp, out)`.
