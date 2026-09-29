import hashlib
import hmac

import pytest

from provenance.db.security import principal_sql

KEY = "ab" * 32


def test_groups_are_sorted_and_deduplicated_before_signing() -> None:
    _, (groups, _) = principal_sql(["b_team", "a_team", "b_team"], KEY)

    assert groups == "a_team,b_team"


def test_signature_is_hmac_sha256_of_the_group_string() -> None:
    _, (groups, sig) = principal_sql(["analyst_tech"], KEY)

    assert sig == hmac.new(KEY.encode(), groups.encode(), hashlib.sha256).hexdigest()


def test_settings_are_transaction_scoped() -> None:
    sql, _ = principal_sql(["x"], KEY)

    assert sql.count(", true)") == 2


@pytest.mark.parametrize("bad", ["a,b", "Admin", "x y", "", "a;drop"])
def test_rejects_group_names_that_could_smuggle_extra_groups(bad: str) -> None:
    with pytest.raises(ValueError):
        principal_sql([bad], KEY)


def test_rejects_empty_group_list() -> None:
    with pytest.raises(ValueError):
        principal_sql([], KEY)
