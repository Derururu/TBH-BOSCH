from __future__ import annotations

import os
import shutil
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path("onedrive_gdpr_pdf_test_set")
TARGET_TOTAL_BYTES = 1024 * 1024 * 1024


SECTIONS = {
    "Expense_Report": {
        "template": [
            "Expense Form",
            "Purpose: Expense reimbursement.",
            "Employee: ______",
            "Expense: ______",
            "Amount: ______",
            "Date: ______",
            "",
            "Expense Form",
            "Purpose: Expense reimbursement.",
            "Summary: ______",
            "Approval: ______",
            "Signature: ______",
        ],
        "Example_A": [
            "Expense Reimbursement (Filled)",
            "Purpose: Example of a completed expense reimbursement record.",
            "Employee: Sara Hoffmann (E-20491)",
            "Department: Project Management",
            "Date: 10 May 2026",
            "Category: Travel",
            "Amount: 128.40 EUR",
            "Description: Train ticket for customer workshop (round trip).",
            "",
            "Expense Reimbursement (Filled) - Review",
            "Summary: Total claimed: 128.40 EUR. Receipts attached.",
            "Manager: Philipp Neumann",
            "Decision: Approved",
            "Date: 12 May 2026",
        ],
        "Example_B": [
            "Expense Reimbursement (Filled)",
            "Purpose: Example of a completed expense reimbursement record.",
            "Employee: David Schmid (E-31705)",
            "Department: Engineering",
            "Date: 06 May 2026",
            "Category: Meals",
            "Amount: 24.90 EUR",
            "Description: Meal during approved business trip.",
            "",
            "Expense Reimbursement (Filled) - Review",
            "Summary: Total claimed: 24.90 EUR. Policy limits checked.",
            "Manager: Laura Koenig",
            "Decision: Approved",
            "Date: 08 May 2026",
        ],
    },
    "IT_Access_Request": {
        "template": [
            "IT System Access Request Form",
            "Purpose: Used to request IT system access.",
            "Name: ______",
            "Department: ______",
            "System: ______",
            "Access Level: ______",
            "Justification: ______",
            "",
            "IT System Access Request Form",
            "IT Review: ______",
            "Comments: ______",
            "Approval: ______",
            "Final Signature: ______",
        ],
        "Example_A": [
            "IT System Access Request (Filled)",
            "Purpose: Example of a completed IT access request for audit trail and governance.",
            "Name: Elena Fischer",
            "Department: Digital Operations",
            "Manager: Jonas Keller",
            "System: Document Management Portal",
            "Access Level: Editor",
            "Justification: Required to maintain project documentation and manage controlled templates.",
            "",
            "IT System Access Request (Filled) - Review",
            "Reviewer: IT Service Desk",
            "Comments: Access aligns with role; MFA verified.",
            "Approval: Approved",
            "Approver: IT Governance Lead",
            "Signature: J. Keller",
            "Date: 19 May 2026",
        ],
        "Example_B": [
            "IT System Access Request (Filled)",
            "Purpose: Example of a completed IT access request for audit trail and governance.",
            "Name: Tobias Wagner",
            "Department: Compliance & Risk",
            "Manager: Miriam Braun",
            "System: GRC Role Catalog",
            "Access Level: Viewer",
            "Justification: Needed for audit preparation and role verification activities.",
            "",
            "IT System Access Request (Filled) - Review",
            "Reviewer: Identity & Access Team",
            "Comments: Least-privilege confirmed; access time-limited.",
            "Approval: Approved",
            "Approver: Compliance Officer",
            "Signature: M. Braun",
            "Date: 19 May 2026",
        ],
    },
    "Incident_Report": {
        "template": [
            "Incident Report",
            "Purpose: Record incident.",
            "Date: ______",
            "Location: ______",
            "Description: ______",
            "",
            "Incident Report",
            "Purpose: Record incident.",
            "Cause: ______",
            "Action: ______",
            "Owner: ______",
        ],
        "Example_A": [
            "Incident Report (Filled)",
            "Purpose: Example of a documented incident for compliance review.",
            "Date: 05 May 2026",
            "Location: Office Floor 3",
            "Type: Data Handling",
            "Description: A document containing personal data was mistakenly shared to an incorrect internal distribution list.",
            "",
            "Incident Report (Filled) - Review",
            "Root Cause: Incorrect selection of recipient group during email composition; no secondary review step.",
            "Corrective Action: Introduce a mandatory recipient review checklist",
            "Owner: Team Lead",
            "Deadline: 30 May 2026",
        ],
        "Example_B": [
            "Incident Report (Filled)",
            "Purpose: Example of a documented incident for compliance review.",
            "Date: 28 Apr 2026",
            "Location: Meeting Room A",
            "Type: Safety",
            "Description: Minor slip incident near entrance due to wet floor; no injury reported.",
            "",
            "Incident Report (Filled) - Review",
            "Root Cause: Cleaning sign placed after area was already wet; timing issue.",
            "Corrective Action: Update cleaning SOP to place signage before wet cleaning",
            "Owner: Facility Coordinator",
            "Deadline: 20 May 2026",
        ],
    },
    "Supplier_Onboarding": {
        "template": [
            "Supplier Onboarding",
            "Purpose: Setup supplier.",
            "Company: ______",
            "Contact: ______",
            "Tax ID: ______",
            "",
            "Supplier Onboarding",
            "Purpose: Setup supplier.",
            "Review: ______",
            "Approval: ______",
            "Notes: ______",
        ],
        "Example_A": [
            "Supplier Onboarding (Filled)",
            "Purpose: Example of a completed supplier onboarding record.",
            "Company: Nordic Components GmbH",
            "Address: Hauptstr. 12, 70173 Stuttgart",
            "Contact: procurement@nordic-components.example",
            "Tax ID: DE123456789",
            "Certification: ISO 9001",
            "Risk Level: Medium",
            "",
            "Supplier Onboarding (Filled) - Review",
            "Reviewer: Procurement Ops",
            "Comments: Documents verified; banking details pending validation.",
            "Approval: Conditionally Approved",
            "Notes: Activate vendor after bank verification.",
        ],
        "Example_B": [
            "Supplier Onboarding (Filled)",
            "Purpose: Example of a completed supplier onboarding record.",
            "Company: Alpine Services AG",
            "Address: Industriestr. 8, 80331 Munich",
            "Contact: vendor@alpine-services.example",
            "Tax ID: DE987654321",
            "Certification: ISO 27001",
            "Risk Level: Low",
            "",
            "Supplier Onboarding (Filled) - Review",
            "Reviewer: Vendor Management",
            "Comments: All compliance checks passed.",
            "Approval: Approved",
            "Notes: Eligible for standard payment terms.",
        ],
    },
    "Training_Evaluation": {
        "template": [
            "Training Evaluation",
            "Purpose: Evaluate training.",
            "Name: ______",
            "Course: ______",
            "Rating: ______",
            "",
            "Training Evaluation",
            "Purpose: Evaluate training.",
            "Comments: ______",
            "Recommendation: ______",
        ],
        "Example_A": [
            "Training Evaluation (Filled)",
            "Purpose: Example of a completed training feedback form.",
            "Participant: Nina Beck",
            "Course: Data Protection Basics",
            "Date: 14 May 2026",
            "Content: 5/5",
            "Trainer: 4/5",
            "Material: 4/5",
            "",
            "Training Evaluation (Filled) - Review",
            "Comments: Clear structure and helpful examples; add more hands-on exercises.",
            "Recommendation: Repeat quarterly for new joiners.",
        ],
        "Example_B": [
            "Training Evaluation (Filled)",
            "Purpose: Example of a completed training feedback form.",
            "Participant: Markus Steiner",
            "Course: Document Classification Workshop",
            "Date: 16 May 2026",
            "Content: 4/5",
            "Trainer: 5/5",
            "Material: 3/5",
            "",
            "Training Evaluation (Filled) - Review",
            "Comments: Trainer excellent; slides were dense - provide a cheat sheet.",
            "Recommendation: Add a short pre-read and a 15-min quiz.",
        ],
    },
}


def reset_root() -> None:
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)


def write_pdf(path: Path, lines: list[str]) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 58
    for idx, line in enumerate(lines):
        if idx == 0:
            c.setFont("Helvetica-Bold", 15)
        elif line.endswith("(Filled)") or line.endswith("Review") or line in SECTIONS:
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 10)
        if not line:
            y -= 10
            continue
        c.drawString(54, y, line[:118])
        y -= 18
        if y < 54:
            c.showPage()
            y = height - 58
    c.save()


def pad_file(path: Path, target_size: int) -> None:
    current = path.stat().st_size
    if current >= target_size:
        return
    remaining = target_size - current
    with path.open("ab") as f:
        while remaining > 0:
            chunk = min(1024 * 1024, remaining)
            f.write(os.urandom(chunk))
            remaining -= chunk


def build_dataset() -> None:
    reset_root()
    outputs: list[Path] = []
    for section, docs in SECTIONS.items():
        section_dir = ROOT / section
        section_dir.mkdir()
        for variant, lines in docs.items():
            filename = f"{section}.pdf" if variant == "template" else f"{section}_{variant}.pdf"
            path = section_dir / filename
            write_pdf(path, lines)
            outputs.append(path)

    base_total = sum(path.stat().st_size for path in outputs)
    padding_needed = max(0, TARGET_TOTAL_BYTES - base_total)
    per_file, extra = divmod(padding_needed, len(outputs))
    for idx, path in enumerate(outputs):
        pad_file(path, path.stat().st_size + per_file + (1 if idx < extra else 0))

    notes = ROOT / "README_DATASET.txt"
    notes.write_text(
        "Synthetic GDPR PDF test set based on the section pattern from a-klumpp/GDPR-data-samples.\n"
        "Sections: Expense_Report, IT_Access_Request, Incident_Report, Supplier_Onboarding, Training_Evaluation.\n"
        "Each section contains one blank template and two filled examples.\n"
        "Files are padded with random bytes to reach about 1 GiB total for OneDrive sync testing.\n"
        "All visible data is synthetic and must not be used as real personal/business data.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build_dataset()
    total = sum(path.stat().st_size for path in ROOT.rglob("*") if path.is_file())
    print(f"Generated {total} bytes in {ROOT.resolve()}")
