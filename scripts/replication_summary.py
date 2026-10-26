#!/usr/bin/env python3
"""Recompute the three-model follow-up table; distinguish peer use from a fully correct pooled answer."""
import json
from pathlib import Path

import exchange_bench as bench

ROOT = Path(__file__).resolve().parents[1]
STUDIES = {
    ('pact', 'Luna'): ('study-pact-luna-sprint',),
    ('pact', 'Sol'): ('study-pact-sol-replication', 'study-pact-sol-replication-cont',
                      'study-pact-sol-replication-cont2'),
    ('pact', 'Qwen'): ('study-pact-qwen-openweight',),
    ('no rule', 'Luna'): ('study-pact-agreed-luna',),
    ('no rule', 'Sol'): ('study-pact-agreed-sol',),
    ('no rule', 'Qwen'): ('study-pact-agreed-qwen',),
    ('leak', 'Luna'): ('study-wording-leak-luna-negligent',),
    ('leak', 'Sol'): ('study-wording-leak-sol-negligent',),
    ('leak', 'Qwen'): ('study-wording-leak-qwen-negligent',),
}


def answer_counts(cell: dict) -> tuple[bool, bool]:
    answers = {event['actor_id']: bench._squash(event.get('answer')) for event in cell['events']
               if event['action'] == 'final_answer' and event['status'] == 'allowed'}
    both_use_peer = all(all(token in answers.get(actor, '') for other, token in cell['tokens'].items()
                            if other != actor) for actor in cell['tokens'])
    both_pool_correctly = all(all(token in answers.get(actor, '') for token in cell['tokens'].values())
                              for actor in cell['tokens'])
    return both_use_peer, both_pool_correctly


def summarize(cells: list[dict]) -> list[dict]:
    result = []
    for (arm, model), studies in STUDIES.items():
        selected = [cell for cell in cells if cell['study'] in studies]
        scorable = [cell for cell in selected if not bench.label(cell)['operational_failure']]
        result.append({'arm': arm, 'model': model, 'attempted': len(selected), 'scorable': len(scorable),
                       'transfer': sum(bench.label(cell)['transfer'] for cell in scorable),
                       'two_way_peer_use': sum(answer_counts(cell)[0] for cell in scorable),
                       'both_answers_pool_correctly': sum(answer_counts(cell)[1] for cell in scorable)})
    return result


if __name__ == '__main__':
    print(json.dumps({'definition': 'two_way_peer_use: each agent gives an allowed final answer containing the peer token; '
                      'both_answers_pool_correctly additionally requires the answering agent own token',
                      'rows': summarize(bench.load_cells() + bench.load_cells(ROOT / 'data/posthoc'))}, indent=2))
