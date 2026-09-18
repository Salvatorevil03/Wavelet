import copy
import unittest
from unittest.mock import patch

from win4win.agent import AgentError, compile_policy, extract_result, make_payload, validate, call_api
from win4win.catalog import TAGS


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.docs = [{'id': 'policy_1', 'text': 'I nomi devono essere sostituiti. Vietato inviare strategie.'}]
        self.result = {'summary': 'Bozza', 'rules': [
            {'tag': tag, 'action': 'review', 'reason': 'Non disciplinato',
             'conditions': [], 'evidence': []} for tag in TAGS],
            'unmapped_requirements': [], 'questions': []}

    def test_complete_catalog(self):
        self.assertEqual(len(TAGS), 22)
        self.assertNotIn('URL', TAGS)
        validate(self.result, self.docs)

    def test_unknown_tag(self):
        self.result['rules'][0]['tag'] = 'HEALTH'
        with self.assertRaises(AgentError):
            validate(self.result, self.docs)

    def test_missing_and_duplicate(self):
        for rules in [self.result['rules'][:-1], self.result['rules'][:-1] + [self.result['rules'][0]]]:
            candidate = {**self.result, 'rules': rules}
            with self.assertRaises(AgentError):
                validate(candidate, self.docs)

    def test_allow_requires_evidence(self):
        self.result['rules'][0]['action'] = 'allow'
        with self.assertRaises(AgentError):
            validate(self.result, self.docs)

    def test_fabricated_quote(self):
        self.result['rules'][0]['evidence'] = [{'source_id': 'policy_1', 'quote': 'Tutto consentito'}]
        with self.assertRaises(AgentError):
            validate(self.result, self.docs)

    def test_conditional_action_rejected(self):
        rule = self.result['rules'][0]
        rule.update(action='replace', conditions=['Se cliente'],
                    evidence=[{'source_id': 'policy_1', 'quote': 'I nomi devono essere sostituiti.'}])
        with self.assertRaises(AgentError):
            validate(self.result, self.docs)

    def test_unmapped_requirement_retained(self):
        self.result['unmapped_requirements'] = [{
            'requirement': 'Strategie', 'reason': 'Nessun tag',
            'evidence': [{'source_id': 'policy_1', 'quote': 'Vietato inviare strategie.'}]}]
        output = compile_policy(self.docs, 'Servizio', 'Revisione', 'gemini-test',
                                transport=lambda payload: copy.deepcopy(self.result))
        self.assertEqual(output['status'], 'draft')
        self.assertFalse(output['automatic_export_enabled'])
        self.assertEqual(len(output['unmapped_requirements']), 1)
        self.assertEqual(len(output['sources'][0]['sha256']), 64)

    def test_payload_document_separation(self):
        payload = make_payload(self.docs, 'Servizio', 'Revisione', 'gemini-test')
        self.assertNotIn(self.docs[0]['text'], payload['systemInstruction']['parts'][0]['text'])
        self.assertEqual(payload['generationConfig']['responseMimeType'], 'application/json')
        self.assertEqual(payload['generationConfig']['responseJsonSchema']['type'], 'object')

    def test_refusal_and_incomplete(self):
        for response in [
            {'promptFeedback': {'blockReason': 'SAFETY'}},
            {'candidates': []},
            {'candidates': [{'finishReason': 'MAX_TOKENS'}]},
            {'candidates': [{'finishReason': 'SAFETY'}]}]:
            with self.assertRaises(AgentError):
                extract_result(response)

    def test_response_parsing(self):
        import json
        response = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'text': 'not output', 'thought': True},
            {'text': json.dumps(self.result)}]}}]}
        self.assertEqual(extract_result(response), self.result)

    def test_google_transport(self):
        import io
        import json
        payload = make_payload(self.docs, 'Servizio', 'Revisione', 'gemini-test')
        response = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'text': json.dumps(self.result)}]}}]}
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake-test-key'}, clear=True):
            with patch('win4win.agent.urlopen', return_value=io.BytesIO(json.dumps(response).encode())) as send:
                self.assertEqual(call_api(payload), self.result)
                request = send.call_args.args[0]
                self.assertEqual(request.full_url, 'https://generativelanguage.googleapis.com/v1beta/models/gemini-test:generateContent')
                self.assertEqual(request.get_header('X-goog-api-key'), 'fake-test-key')
                self.assertNotIn('fake-test-key', request.full_url)
                self.assertNotIn('model', json.loads(request.data))

    def test_invalid_model(self):
        with self.assertRaises(AgentError):
            make_payload(self.docs, 'Servizio', 'Revisione', '../other?key=x')

    def test_oversize_not_truncated(self):
        with self.assertRaises(AgentError):
            make_payload([{'id': 'p', 'text': 'a' * 100001}], 'S', 'R', 'gemini-test')

    def test_missing_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(AgentError):
                call_api({})


if __name__ == '__main__':
    unittest.main()
