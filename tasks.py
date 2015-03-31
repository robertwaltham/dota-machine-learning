from __future__ import absolute_import

from celery import shared_task

from website.celery import app
from DotaStats.models import Match

@app.task
def get_details(match_id):
    print match_id
    match = Match.objects.get(match_id=match_id)
    if match and not match.has_been_processed:
        match.load_details_from_api()
    return match_id

