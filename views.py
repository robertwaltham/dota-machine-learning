from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, View, TemplateView
from django.views.generic.edit import FormView

from models import Match

import json
import urllib2
import datetime

from django.http import HttpResponse

key = '8F60050E57157048213A74F8D0F08EFA'
api_base = 'https://api.steampowered.com'
match_history = '/IDOTA2Match_570/GetMatchHistory/V001/?min_players=10&matches_requested=25&key='
details = '/IDOTA2Match_570/GetMatchDetails/V001/?match_id=%s&key=%s'


class IndexView(TemplateView):
    template_name = 'DotaStats/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['matches'] = Match.get_all()
        return context


def get_match(request):
    url = api_base + match_history + key
    data = json.load(urllib2.urlopen(url))

    result = ''

    if data['result']['status'] == 1:
        for match in data['result']['matches']:
            start_time = datetime.datetime.fromtimestamp(match['start_time'])
            result += "%s %s %s\n" % (match['match_id'], match['match_seq_num'],
                                      start_time.strftime('%Y-%m-%d %H:%M:%S'))
            new_match = Match()
            new_match.match_id = match['match_id']
            new_match.match_seq_num = match['match_seq_num']
            new_match.start_time = start_time
            new_match.lobby_type = match['lobby_type']
            new_match.save()

    return HttpResponse("<pre>" + url + "\n" + result + "</pre>")

