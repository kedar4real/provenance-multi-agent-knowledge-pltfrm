from provenance.ingest.sections import extract_items, html_to_text

BODY_1 = "Apple designs smartphones. " * 40
BODY_1A = "Supply chain disruption could hurt results. " * 60
BODY_7 = "Net sales increased due to higher iPhone revenue. " * 50

FILING = f"""
Table of Contents
Item 1.
Business
3
Item 1A.
Risk Factors
5
Item 7.
Management's Discussion and Analysis of Financial Condition and Results of Operations
20
Item 1. Business
{BODY_1}
See Part II, Item 7, "Management's Discussion and Analysis" for more.
Item 1A. Risk Factors
{BODY_1A}
Item 1B. Unresolved Staff Comments
None.
Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
{BODY_7}
Item 7A. Quantitative and Qualitative Disclosures About Market Risk
Interest rate risk text.
"""


def test_extracts_the_body_sections_not_the_table_of_contents() -> None:
    items = extract_items(FILING)

    assert set(items) == {"1", "1A", "7"}
    assert BODY_1A.strip() in items["1A"].text
    assert "Table of Contents" not in items["1"].text


def test_section_ends_at_the_next_item_heading() -> None:
    items = extract_items(FILING)

    assert "Unresolved Staff Comments" not in items["1A"].text
    assert "Interest rate risk" not in items["7"].text


def test_cross_reference_inside_a_sentence_is_not_a_heading() -> None:
    items = extract_items(FILING)

    assert "See Part II, Item 7" in items["1"].text


def test_heading_split_across_lines_is_recognized() -> None:
    text = f"Item 1A.\nRisk Factors\n{BODY_1A}\nItem 2.\nProperties\nOffices."

    assert BODY_1A.strip() in extract_items(text)["1A"].text


def test_records_title_and_offsets_into_the_full_text() -> None:
    items = extract_items(FILING)
    section = items["1A"]

    assert section.title == "Risk Factors"
    assert FILING[section.char_start : section.char_end] == section.text


def test_running_page_headers_do_not_split_a_section() -> None:
    page_1, page_2 = "Azure grew strongly. " * 30, "LinkedIn revenue rose. " * 30
    text = (
        f"Item 1. Business\n{page_1}\nPART I\nItem 1\nLinkedIn\n{page_2}\n"
        f"Item 1A. Risk Factors\n{BODY_1A}"
    )

    section = extract_items(text)["1"]

    assert page_1.strip() in section.text and page_2.strip() in section.text
    assert "\nItem 1\n" not in section.text and "PART I" not in section.text


def test_mdna_incorporated_by_reference_falls_back_to_the_standalone_section() -> None:
    mdna = "Net interest income rose on higher rates. " * 80
    text = (
        f"Item 1A. Risk Factors\n{BODY_1A}\n"
        "Item 7. Management's Discussion and Analysis of Financial Condition\n"
        'Reference is made to the section entitled "Management\'s Discussion and Analysis".\n'
        "Item 8. Financial Statements and Supplementary Data\nSee the Financial Section.\n"
        "FINANCIAL SECTION\n"
        "MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS\n"
        f"{mdna}\n"
        "Report of Independent Registered Public Accounting Firm\nWe audited the statements.\n"
    )

    section = extract_items(text)["7"]

    assert mdna.strip() in section.text
    assert "Reference is made" not in section.text
    assert "We audited" not in section.text


def test_mdna_subsection_named_like_a_statement_does_not_end_it() -> None:
    overview, analysis = "Executive overview text. " * 60, "Balance sheet discussion. " * 60
    text = (
        "Item 7. Management's Discussion and Analysis\nSee the Annual Report section.\n"
        "Item 8. Financial Statements and Supplementary Data\nSee below.\n"
        f"Management's discussion and analysis\n{overview}\n"
        f"Consolidated Balance Sheets and Cash Flows Analysis\n{analysis}\n"
        "Consolidated Balance Sheets\nAssets 100\n"
    )

    section = extract_items(text)["7"]

    assert overview.strip() in section.text and analysis.strip() in section.text
    assert "Assets 100" not in section.text


def test_missing_item_is_simply_absent() -> None:
    assert "7" not in extract_items(f"Item 1A. Risk Factors\n{BODY_1A}")


def test_html_to_text_drops_page_footers_and_bare_page_numbers() -> None:
    html = """<html><body><div>Item 1A. Risk Factors</div>
    <div>Risks are real.</div><div>Apple Inc. | 2025 Form 10-K | 20</div><div>21</div>
    <div>More risks.</div><script>x=1</script></body></html>"""

    text = html_to_text(html)

    assert "Risks are real." in text and "More risks." in text
    assert "Form 10-K |" not in text
    assert "\n21\n" not in f"\n{text}\n"
    assert "x=1" not in text


def test_html_to_text_normalizes_non_breaking_spaces() -> None:
    assert html_to_text("<p>Item\xa01A.&nbsp;Risk</p>") == "Item 1A. Risk"
