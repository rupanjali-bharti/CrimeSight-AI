import unittest

from evidence_matcher import analyze_case_evidence


class EvidenceMatcherTests(unittest.TestCase):
    def test_harassment_follow_up_selects_cyber_evidence(self):
        result = analyze_case_evidence(
            "They keep threatening me. I saved screenshots of the fake profile, "
            "the threatening chat thread, call logs, and a link to the defamatory post.",
            [
                {
                    "role": "user",
                    "content": "Someone made a fake profile and sends abusive messages.",
                },
                {
                    "role": "assistant",
                    "content": "Could you provide evidence?",
                },
            ],
        )

        self.assertEqual(result["category"], "cyber_harassment")
        self.assertEqual(result["category_label"], "Cyber Harassment / Stalking")
        self.assertEqual(
            [item["status"] for item in result["evidence_checklist"]],
            ["AVAILABLE", "AVAILABLE", "AVAILABLE", "AVAILABLE"],
        )

    def test_financial_follow_up_uses_financial_evidence(self):
        result = analyze_case_evidence(
            "I have the SMS bank debit alert, UTR 812345, UPI ID merchant@bank, "
            "and bank statement.",
            [{"role": "user", "content": "I lost money in a UPI scam."}],
        )

        self.assertEqual(result["category"], "financial_fraud")
        self.assertEqual(
            [item["status"] for item in result["evidence_checklist"]],
            ["AVAILABLE", "AVAILABLE", "AVAILABLE", "AVAILABLE"],
        )

    def test_cyber_signals_outweigh_incidental_financial_terms(self):
        result = analyze_case_evidence(
            "A fake profile sends abusive messages and threats. They mentioned "
            "money but no bank transaction happened."
        )

        self.assertEqual(result["category"], "cyber_harassment")

    def test_later_denial_keeps_evidence_missing(self):
        result = analyze_case_evidence(
            "I do not have the threatening chat screenshots.",
            [{"role": "user", "content": "I have screenshots of threatening chats."}],
        )

        self.assertEqual(result["category"], "cyber_harassment")
        self.assertEqual(result["evidence_checklist"][1]["status"], "MISSING")

    def test_latest_evidence_mention_in_a_turn_controls_status(self):
        result = analyze_case_evidence(
            "There is a fake profile. I have screenshots of the fake profile, "
            "but I do not have screenshots of the fake profile."
        )

        self.assertEqual(result["category"], "cyber_harassment")
        self.assertEqual(result["evidence_checklist"][0]["status"], "MISSING")

    def test_non_user_history_does_not_affect_case_classification(self):
        result = analyze_case_evidence(
            "A fake profile is stalking me and sending abusive messages.",
            [
                {
                    "role": "assistant",
                    "content": "This sounds like a bank fraud involving UPI.",
                }
            ],
        )

        self.assertEqual(result["category"], "cyber_harassment")

    def test_hacking_and_data_breach_select_cyber_fraud_category(self):
        result = analyze_case_evidence(
            "Someone hacked my email account, stole my credentials, and exposed "
            "my personal data in a data breach."
        )

        self.assertEqual(result["category"], "cyber_fraud_impersonation")
        self.assertEqual(result["category_label"], "Cyber Fraud / Impersonation")

    def test_impersonation_for_financial_gain_selects_cyber_fraud_category(self):
        result = analyze_case_evidence(
            "A person is impersonating me with a fake account to scam my contacts."
        )

        self.assertEqual(result["category"], "cyber_fraud_impersonation")

    def test_cyber_fraud_evidence_updates_from_full_user_history(self):
        result = analyze_case_evidence(
            "I have the login notification, IP address and access logs, phishing "
            "message link, and transaction receipt.",
            [{"role": "user", "content": "Someone hacked my account."}],
        )

        self.assertEqual(result["category"], "cyber_fraud_impersonation")
        self.assertEqual(
            [item["status"] for item in result["evidence_checklist"]],
            ["AVAILABLE", "AVAILABLE", "AVAILABLE", "AVAILABLE"],
        )

    def test_witness_and_incident_details_are_detected_semantically(self):
        result = analyze_case_evidence(
            "The assault happened around 8:30 pm near Central Park. "
            "My colleague Aman saw what happened.",
            [
                {
                    "role": "user",
                    "content": "I was attacked yesterday evening.",
                }
            ],
        )

        checklist = {item["item"]: item["status"] for item in result["evidence_checklist"]}
        self.assertEqual(checklist["Witness details / statements"], "AVAILABLE")
        self.assertEqual(checklist["Incident time and location"], "AVAILABLE")

    def test_incident_details_accumulate_across_conversation_turns(self):
        result = analyze_case_evidence(
            "My neighbor Riya was there and saw the assault.",
            [
                {"role": "user", "content": "I was assaulted."},
                {"role": "assistant", "content": "When and where did this happen?"},
                {"role": "user", "content": "It happened yesterday at 6 pm in Delhi."},
            ],
        )

        checklist = {item["item"]: item["status"] for item in result["evidence_checklist"]}
        self.assertEqual(checklist["Witness details / statements"], "AVAILABLE")
        self.assertEqual(checklist["Incident time and location"], "AVAILABLE")

    def test_fir_ready_is_true_only_when_every_item_is_available(self):
        result = analyze_case_evidence(
            "The assault happened on 12 August 2026 at 8:30 pm in Delhi. "
            "My neighbor Riya witnessed it and gave a statement. "
            "I have the hospital medical report and CCTV video footage."
        )

        self.assertTrue(result["fir_ready"])
        self.assertTrue(
            all(item["status"] == "AVAILABLE" for item in result["evidence_checklist"])
        )

    def test_incident_time_and_location_item_requires_both_details(self):
        for narrative in (
            "The assault happened around 8:30 pm.",
            "The assault happened near Central Park.",
        ):
            with self.subTest(narrative=narrative):
                result = analyze_case_evidence(narrative)
                incident_item = next(
                    item
                    for item in result["evidence_checklist"]
                    if item["item"] == "Incident time and location"
                )
                self.assertEqual(incident_item["status"], "MISSING")

    def test_contract_dispute_replaces_previous_category_checklist(self):
        result = analyze_case_evidence(
            "This is actually a commercial contract fraud: the vendor took payment "
            "and never handed over the source code.",
            [
                {
                    "role": "user",
                    "content": "A former partner is harassing me online.",
                }
            ],
        )

        self.assertEqual(result["category"], "commercial_contract_fraud")
        self.assertEqual(result["category_label"], "Commercial / Contract Fraud")
        self.assertEqual(
            [item["item"] for item in result["evidence_checklist"]],
            [
                "Contracts / agreements and amendments",
                "Emails / written correspondence",
                "Invoices / payment statements",
                "Deliverables / code handover records",
                "Witness / meeting statements",
            ],
        )
        self.assertNotIn(
            "Threatening chat threads",
            [item["item"] for item in result["evidence_checklist"]],
        )

    def test_commercial_evidence_is_found_across_follow_up_turns(self):
        result = analyze_case_evidence(
            "I also have the project handover email and source-code repository access "
            "transfer, plus a written statement from our project manager.",
            [
                {"role": "user", "content": "This is a commercial contract fraud."},
                {"role": "assistant", "content": "Do you have supporting records?"},
                {
                    "role": "user",
                    "content": "I found the signed agreement, invoice, and bank statement.",
                },
            ],
        )

        self.assertEqual(result["category"], "commercial_contract_fraud")
        checklist = {item["item"]: item["status"] for item in result["evidence_checklist"]}
        self.assertEqual(checklist["Contracts / agreements and amendments"], "AVAILABLE")
        self.assertEqual(checklist["Emails / written correspondence"], "AVAILABLE")
        self.assertEqual(checklist["Invoices / payment statements"], "AVAILABLE")
        self.assertEqual(checklist["Deliverables / code handover records"], "AVAILABLE")
        self.assertEqual(checklist["Witness / meeting statements"], "AVAILABLE")
        self.assertTrue(result["fir_ready"])

    def test_latest_explicit_category_can_replace_older_cyber_case(self):
        result = analyze_case_evidence(
            "Separate matter: the contractor committed commercial contract fraud "
            "by withholding our source code after payment.",
            [{"role": "user", "content": "I am being cyberstalked by a fake profile."}],
        )

        self.assertEqual(result["category"], "commercial_contract_fraud")

    def test_follow_up_document_mention_updates_commercial_document_item(self):
        result = analyze_case_evidence(
            "I found and uploaded the supporting documents from the contract project.",
            [{"role": "user", "content": "The vendor committed contract fraud."}],
        )

        documents_item = next(
            item
            for item in result["evidence_checklist"]
            if item["item"] == "Contracts / agreements and amendments"
        )
        self.assertEqual(documents_item["status"], "AVAILABLE")


if __name__ == "__main__":
    unittest.main()
