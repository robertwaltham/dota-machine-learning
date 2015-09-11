from __future__ import absolute_import

from website.celery import app
from DotaStats.models import Match, ScikitModel
from DotaStats.scikit import DotaModel
from DotaStats.dota import DotaApi

@app.task
def load_matches():
    return DotaApi.load_matches_from_api()

@app.task
def build_model(n_matches, model_id):
    return DotaModel.build_and_store(n_matches, model_id)

@app.task
def build_and_test(starting_match_id, test_match_ids):
    results = DotaModel.build_and_test(starting_match_id, test_match_ids)
    correct = 0
    count = len(results)
    for result in results:
        if result['prediction'] == result['win']:
            correct += 1

    return {"count": count, "correct": correct, "%": (float(correct) / float(count)) * 100}

@app.task
def process_match(match):
    return Match.process_match_info(match)


