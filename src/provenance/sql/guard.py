"""Validate model-written SQL before it runs. The first of three layers: this parser check,
then the read-only `provenance_sql_ro` role, then row-level security on every row.

The SQL is parsed (sqlglot), never pattern-matched: comments, casing, quoting and nesting
can't smuggle a statement past a parser the way they can past a regex.
"""

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

ALLOWED_TABLES = frozenset({"financial_facts", "companies"})
MAX_ROWS = 200

# Plain value functions and aggregates only. Anything else (set_config, current_setting,
# pg_sleep, pg_read_file, dblink, lo_*, ...) is rejected by name.
ALLOWED_FUNCTIONS = frozenset(
    {
        "SUM", "AVG", "MIN", "MAX", "COUNT", "ROUND", "ABS", "COALESCE", "NULLIF",
        "GREATEST", "LEAST", "LAG", "LEAD", "ROW_NUMBER", "RANK", "DENSE_RANK",
        "FIRST_VALUE", "LAST_VALUE", "CAST", "TRYCAST", "LOWER", "UPPER", "LENGTH",
        "CONCAT", "EXTRACT", "IF", "CASE", "DIV", "MOD", "POWER", "POW", "SQRT", "LN",
        "STDDEV", "STDDEV_SAMP", "VARIANCE", "STRING_AGG", "ARRAY_AGG",
    }
)  # fmt: skip

_FORBIDDEN_NODES = (
    exp.Insert, exp.Update, exp.Delete, exp.Merge, exp.Create, exp.Drop, exp.Alter,
    exp.Command, exp.Set, exp.Into, exp.Copy, exp.Grant, exp.TruncateTable, exp.Lock,
)  # fmt: skip


_OPERATORS = (exp.Binary, exp.Connector, exp.Predicate, exp.Unary, exp.Paren)


class UnsafeSQL(ValueError):
    """The model's SQL failed validation; the message is safe to show the model for a retry."""


def guard(sql: str) -> str:
    """Returns the normalized, row-limited SQL, or raises UnsafeSQL explaining why not."""
    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
    except ParseError as e:
        raise UnsafeSQL(f"not valid SQL: {str(e).splitlines()[0]}") from e
    if len(statements) != 1:
        raise UnsafeSQL("exactly one statement is allowed")
    tree = statements[0]
    if not isinstance(tree, exp.Query):
        raise UnsafeSQL("only SELECT queries are allowed")

    for node in tree.walk():
        if isinstance(node, _FORBIDDEN_NODES):
            raise UnsafeSQL(f"{type(node).__name__.upper()} is not allowed")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if table.args.get("db") or table.args.get("catalog"):
            raise UnsafeSQL(f"schema-qualified table {table.sql()} is not allowed")
        if name not in ALLOWED_TABLES and name not in cte_names:
            raise UnsafeSQL(f"table {name!r} is not allowed (use financial_facts, companies)")

    for func in tree.find_all(exp.Func):
        if isinstance(func, _OPERATORS):  # sqlglot models AND, =, +, NOT... as Func too
            continue
        name = (func.name if isinstance(func, exp.Anonymous) else func.sql_name()).upper()
        if name not in ALLOWED_FUNCTIONS:
            raise UnsafeSQL(f"function {name.lower()}() is not allowed")

    return _with_row_limit(tree).sql(dialect="postgres", comments=False)


def _with_row_limit(tree: exp.Query) -> exp.Query:
    limit = tree.args.get("limit")
    current = None
    if isinstance(limit, exp.Limit) and isinstance(limit.expression, exp.Literal):
        current = int(limit.expression.this) if limit.expression.is_int else None
    if current is None or current > MAX_ROWS:
        return tree.limit(MAX_ROWS, copy=True)
    return tree
