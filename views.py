from django.views.generic import DetailView, View, TemplateView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.core import serializers
from django import http
from models import Match
import json


class AJAXListMixin(MultipleObjectMixin):
    def get(self, request, *args, **kwargs):
        return http.HttpResponse(serializers.serialize('json', self.get_queryset()))


class IndexView(TemplateView):
    template_name = 'DotaStats/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['count'] = Match.get_all().count()
        context['matches'] = serializers.serialize('json', Match.get_all())
        context['processed'] = Match.get_count_unprocessed()
        context['wins'] = Match.get_winrate()
        return context


class LoadMatchesFromAPI(AJAXListMixin, ListView):
    def get_queryset(self):
        return Match.get_new_matches_from_api()


class LoadDetailsForMatch(AJAXListMixin, ListView):
    def get_queryset(self):
        match = Match.get_unprocessed_match()
        match.load_details_from_api()
        return [match]


class AjaxGetMatchList(AJAXListMixin, ListView):
    def get_queryset(self):
        return Match.get_all()