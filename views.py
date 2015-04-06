from django.views.generic import DetailView, View, TemplateView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.core import serializers
from django import http
from models import Match, Item, Hero, PlayerInMatch, ScikitModel
import json
import numpy as np
from scikit import DotaModel

from tasks import load_matches


class AJAXListMixin(MultipleObjectMixin):
    def get(self, request, *args, **kwargs):
        return http.HttpResponse(serializers.serialize('json', self.get_queryset()))


class IndexView(TemplateView):
    template_name = 'DotaStats/landing.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['count'] = Match.get_all().count()
        context['matches'] = serializers.serialize('json', Match.get_all())
        context['processed'] = Match.get_count_unprocessed()
        context['wins'] = Match.get_winrate()
        context['models'] = ScikitModel.objects.filter(is_ready=True).count()
        return context


class LoadMatchesFromAPI(TemplateView):
    def get(self, request, *args, **kwargs):
        load_matches.delay()
        return http.HttpResponse(json.dumps({'status': 'ok'}))


class LoadDetailsForMatch(AJAXListMixin, ListView):
    def get_queryset(self):
        match = Match.get_unprocessed_match(1)
        match.load_details_from_api()
        return [match]


class LoadDetailsForAll(AJAXListMixin, ListView):
    def get_queryset(self):
        return Match.batch_process_matches()


class AjaxGetMatchList(AJAXListMixin, ListView):
    def get_queryset(self):
        return Match.get_all()


class LoadStaticDataView(View):
    @staticmethod
    def get(request):
        heroes = Hero.load_heroes_from_api()
        items = Item.load_items_from_api()
        return http.HttpResponse(json.dumps({'heroes': heroes, 'items': items}))


class HeroDetail(DetailView):
    template_name = 'DotaStats/hero.html'
    model = Hero
    context_object_name = 'hero'

    def get_context_data(self, **kwargs):
        context = super(HeroDetail, self).get_context_data(**kwargs)
        context['matches'] = PlayerInMatch.get_player_in_match_for_hero_id(self.object)
        return context


class MatchDetail(DetailView):
    template_name = 'DotaStats/match.html'
    model = Match
    context_object_name = 'match'

    def get_context_data(self, **kwargs):
        context = super(MatchDetail, self).get_context_data(**kwargs)
        data, v = self.object.get_data_array()
        context['data'] = np.array_str(data)
        return context


class BuildDataView(View):
    @staticmethod
    def get(request):
        model = ScikitModel.create_model()
        return http.HttpResponse(json.dumps({'task_id': model.task_id}))


class HeroListView(ListView):
    template_name = 'DotaStats/herolist.html'
    context_object_name = 'heroes'

    def get_queryset(self):
        return Hero.objects.all()


class ItemListView(ListView):
    template_name = 'DotaStats/itemlist.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.all()


class MatchList(ListView):
    template_name = 'DotaStats/matchlist.html'
    context_object_name = 'matches'
    model = Match
    paginate_by = 50
    queryset = Match.objects.all().order_by('-match_id')