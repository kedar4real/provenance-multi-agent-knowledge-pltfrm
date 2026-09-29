import hashlib
import hmac
import re

_GROUP = re.compile(r"^[a-z0-9_]{1,64}$")

_PRINCIPAL_SQL = "SELECT set_config('app.groups', %s, true), set_config('app.groups_sig', %s, true)"


def principal_sql(groups: list[str], signing_key: str) -> tuple[str, tuple[str, str]]:
    """SQL + params that attach a caller's access groups to the current transaction.

    The group list is HMAC-signed so the database's row-level-security function can reject a
    list changed later in the transaction (e.g. by model-generated SQL calling set_config).
    Settings are transaction-scoped (`true`), so pooled connections can't leak a principal.
    """
    if not groups:
        raise ValueError("a principal needs at least one access group")
    for group in groups:
        if not _GROUP.match(group):
            raise ValueError(f"invalid access group name {group!r}")
    joined = ",".join(sorted(set(groups)))
    signature = hmac.new(signing_key.encode(), joined.encode(), hashlib.sha256).hexdigest()
    return _PRINCIPAL_SQL, (joined, signature)
