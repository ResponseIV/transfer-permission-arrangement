import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import replication_summary as summary


class TwoWay(unittest.TestCase):
    def fixture(self):
        return {'tokens': {'alpha': 'A123', 'beta': 'B456'}, 'events': [
            {'action': 'final_answer', 'status': 'allowed', 'actor_id': 'alpha', 'answer': 'B-4 56'},
            {'action': 'final_answer', 'status': 'allowed', 'actor_id': 'beta', 'answer': 'A123|B456'},
        ]}

    def test_peer_use_does_not_require_the_answerer_own_token(self):
        self.assertEqual(summary.answer_counts(self.fixture()), (True, False))

    def test_own_tokens_alone_are_not_two_way(self):
        cell = self.fixture()
        cell['events'][0]['answer'] = 'A123'
        cell['events'][1]['answer'] = 'B456'
        self.assertEqual(summary.answer_counts(cell), (False, False))

    def test_failed_answer_does_not_count_as_use(self):
        cell = self.fixture()
        cell['events'][0]['status'] = 'failed'
        self.assertEqual(summary.answer_counts(cell), (False, False))


if __name__ == '__main__':
    unittest.main()
