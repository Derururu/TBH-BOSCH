from __future__ import annotations

from src.classifier import extract_entities
from src.fusion import UnifiedScanner
from src.models import PageContent


def _findings_for(text: str):
    return extract_entities(text, [PageContent(page_number=1, text=text)])


def test_classifier_matches_regex_scanner_contextual_pii() -> None:
    text = "\n".join([
        "Employee: Sara Hoffmann (E-20491)",
        "Name: Elena Fischer",
        "Participant: Nina Beck",
        "Address: Hauptstr. 12, 70173 Stuttgart",
        "Contact: procurement@nordic-components.example",
        "Tax ID: DE123456789",
    ])

    findings = _findings_for(text)
    by_type = {}
    for finding in findings:
        by_type.setdefault(finding.type, set()).add(finding.value)

    assert "Sara Hoffmann" in by_type["name"]
    assert "Elena Fischer" in by_type["name"]
    assert "Nina Beck" in by_type["name"]
    assert "E-20491" in by_type["employee_id"]
    assert "Hauptstr. 12, 70173 Stuttgart" in by_type["address"]
    assert "procurement@nordic-components.example" in by_type["email"]
    assert "DE123456789" in by_type["tax_id"]
    assert "123456789" not in by_type.get("phone", set())


def test_classifier_semantic_phone_does_not_reintroduce_tax_id_false_positive() -> None:
    text = "Supplier contact at procurement@nordic-components.example. Tax ID: DE123456789."
    findings = _findings_for(text)

    phones = [finding.value for finding in findings if finding.type == "phone"]
    assert phones == []


def test_classifier_semantic_phone_still_detects_contextual_phone() -> None:
    text = "Please call support at +49 170 1234567 before closing the ticket."
    findings = _findings_for(text)

    phones = [finding for finding in findings if finding.type == "phone"]
    assert len(phones) == 1
    assert phones[0].value == "+49 170 1234567"
    assert phones[0].flag_type == "Semantic_Match"


def test_classifier_blank_templates_are_not_flagged_as_contextual_pii() -> None:
    text = "Name: ______\nEmployee: ______\nAddress: ______\nParticipant: ______\nSignature: ______"
    findings = _findings_for(text)

    assert [
        finding
        for finding in findings
        if finding.type in {"name", "address", "employee_id", "signature"}
    ] == []


def test_unified_scanner_keeps_regex_and_semantic_rules_aligned() -> None:
    scanner = UnifiedScanner()
    text = "\n".join([
        "Supplier Onboarding",
        "Name: ______",
        "Signature: ______",
        "Tax ID: DE123456789",
        "Contact: procurement@nordic-components.example",
        "Address: Hauptstr. 12, 70173 Stuttgart",
    ])

    result = scanner.scan(text)
    by_type = {}
    for finding in result.findings:
        by_type.setdefault(finding["type"], set()).add(finding["value"])

    assert "______" not in by_type.get("name", set())
    assert "Signature: ______" not in by_type.get("signature", set())
    assert "123456789" not in by_type.get("phone", set())
    assert "procurement@nordic-components.example" in by_type["email"]
    assert "Address: Hauptstr. 12, 70173 Stuttgart" in by_type["address"]
    assert "DE123456789" in by_type["tax_id"]
