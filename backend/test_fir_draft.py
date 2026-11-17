import unittest

from fir_draft import (
    checklist_is_complete,
    compile_fir_draft,
    extract_case_details,
)


class FirDraftTests(unittest.TestCase):
    def test_generation_requires_nonempty_complete_checklist(self):
        complete = [
            {"item": "Screenshot", "status": "AVAILABLE"},
            {"item": "Call log", "status": "AVAILABLE"},
        ]
        incomplete = [complete[0], {"item": "Call log", "status": "MISSING"}]

        self.assertTrue(checklist_is_complete(complete))
        self.assertFalse(checklist_is_complete(incomplete))
        self.assertFalse(checklist_is_complete([]))

    def test_draft_uses_only_reported_narrative_evidence_and_statutes(self):
        draft = compile_fir_draft(
            case_narrative="A fake account sent me threatening messages.",
            category_label="Cyber Harassment / Stalking",
            evidence_checklist=[
                {"item": "Threatening chat threads", "status": "AVAILABLE"},
                {"item": "Call logs", "status": "MISSING"},
            ],
            matched_statutes=[
                {
                    "section": "351",
                    "title": "Criminal intimidation",
                    "statute": "Bharatiya Nyaya Sanhita, 2023",
                }
            ],
        )

        self.assertIn("A fake account sent me threatening messages.", draft)
        self.assertIn("Threatening chat threads", draft)
        self.assertNotIn("\n- Call logs", draft)
        self.assertIn("Bharatiya Nyaya Sanhita, 2023 Section 351", draft)
        self.assertIn("not a filed FIR", draft)

    def test_extracts_explicit_complainant_jurisdiction_date_and_location(self):
        narrative = (
            "My name is Anjali Sharma. The incident took place on 12 August 2026 "
            "around 8:30 pm near Central Park in Bengaluru. Please direct this to "
            "Cubbon Park Police Station."
        )

        details = extract_case_details(narrative)

        self.assertEqual(details["complainant_name"], "Anjali Sharma")
        self.assertEqual(details["police_station"], "Cubbon Park Police Station")
        self.assertEqual(details["district_city"], "Bengaluru")
        self.assertEqual(details["incident_date"], "12 August 2026")
        self.assertEqual(details["incident_time"], "8:30 pm")
        self.assertEqual(details["incident_location"], "Central Park")

    def test_fir_template_prefills_reported_details_and_keeps_unknowns_explicit(self):
        details = extract_case_details(
            "I am Anjali Sharma. It happened yesterday at 8 pm in Bengaluru."
        )
        draft = compile_fir_draft(
            case_narrative="I am Anjali Sharma. It happened yesterday at 8 pm in Bengaluru.",
            category_label="General Incident",
            evidence_checklist=[],
            matched_statutes=[],
            case_details=details,
        )

        self.assertIn("Complainant: Anjali Sharma", draft)
        self.assertIn("Bengaluru", draft)
        self.assertIn("yesterday, 8 pm", draft)
        self.assertIn("[Police Station]", draft)
        self.assertIn("[Address and contact details]", draft)


if __name__ == "__main__":
    unittest.main()
