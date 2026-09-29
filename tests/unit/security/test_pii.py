import pytest

from provenance.security.pii import RedactedText, redact


def test_redacts_email_addresses() -> None:
    out = redact("Contact investor.relations@apple.com for details.")

    assert out.text == "Contact [EMAIL] for details."
    assert out.counts == {"EMAIL": 1}


@pytest.mark.parametrize(
    "phone",
    ["(408) 996-1010", "408-996-1010", "408.996.1010", "+1 408 996 1010", "+44 20 7946 0958"],
)
def test_redacts_phone_numbers(phone: str) -> None:
    assert redact(f"Call {phone} today.").text == "Call [PHONE] today."


def test_redacts_social_security_numbers() -> None:
    assert redact("SSN 123-45-6789 on file.").text == "SSN [SSN] on file."


@pytest.mark.parametrize("invalid", ["000-12-3456", "666-12-3456", "900-12-3456", "123-00-4567"])
def test_ignores_numbers_that_cannot_be_ssns(invalid: str) -> None:
    assert redact(f"Code {invalid}").text == f"Code {invalid}"


@pytest.mark.parametrize("card", ["4111 1111 1111 1111", "4111-1111-1111-1111", "5500005555555559"])
def test_redacts_card_numbers_that_pass_luhn(card: str) -> None:
    assert redact(f"Card {card} used.").text == "Card [CARD] used."


def test_keeps_year_column_headers_even_when_they_pass_luhn() -> None:
    header = "(in millions) 2025 2024 2025 2024"

    assert redact(header).text == header


def test_keeps_long_numbers_that_fail_luhn() -> None:
    assert redact("Order 4111 1111 1111 1112").text == "Order 4111 1111 1111 1112"


@pytest.mark.parametrize(
    "financial",
    [
        "Net sales were $391,035 million in 2024.",
        "Shares outstanding: 14,840,390,000",
        "Fiscal 2024 ended September 28, 2024.",
        "IRS Employer Identification No. 94-2404110",
        "Commission File Number: 001-36743",
    ],
)
def test_leaves_financial_figures_and_company_identifiers_alone(financial: str) -> None:
    assert redact(financial).text == financial


def test_counts_every_redaction_by_kind() -> None:
    out = redact("a@b.com, c@d.org, 408-996-1010")

    assert out.counts == {"EMAIL": 2, "PHONE": 1}
    assert out.total == 3


def test_redacted_text_cannot_be_constructed_outside_the_redactor() -> None:
    with pytest.raises(TypeError):
        RedactedText("raw text that skipped redaction", {})  # type: ignore[call-arg]


def test_slice_of_redacted_text_stays_redacted() -> None:
    out = redact("Email a@b.com or call 408-996-1010 now.")

    piece = out.slice(0, 13)

    assert isinstance(piece, RedactedText)
    assert piece.text == out.text[0:13]
