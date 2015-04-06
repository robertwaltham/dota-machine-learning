from __future__ import absolute_import

from website.celery import app
from DotaStats.models import Match, ScikitModel
from DotaStats.scikit import DotaModel

@app.task
def get_details(match_id):
    match = Match.objects.get(match_id=match_id)
    if match and not match.has_been_processed:
        match.load_details_from_api()
    return match_id


@app.task
def load_matches():
    return Match.batch_get_matches_from_api()

@app.task
def build_model(n_matches, model_id):
    return DotaModel.build_and_store(n_matches, model_id)


