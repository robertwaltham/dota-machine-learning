import json
import numpy as np

from django.views.generic import DetailView, View, TemplateView, ListView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django import http

from models import Match, Item, Hero, PlayerInMatch, ScikitModel, MatchPrediction
from forms import PredictionForm
from tasks import load_matches
from scikit import DotaModel


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(*args, **kwargs)
        return login_required(view)


class JSONResponseMixin(object):

    def render_to_json_response(self, context, **kwargs):
        return http.JsonResponse(
            self.get_data(context),
            **kwargs
        )

    def get_data(self, context):
        del context['view']
        return context


class JSONView(JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class IndexView(TemplateView):
    template_name = 'DotaStats/landing.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['count'] = Match.get_all().count()
        context['matches'] = []
        context['processed'] = Match.get_count_unprocessed()
        context['models'] = ScikitModel.objects.filter(is_ready=True).count()
        return context


class AjaxLoadMatchesFromAPI(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        Match.get_new_matches_from_api()
        return super(AjaxLoadMatchesFromAPI, self).get_context_data(status='ok', **kwargs)


class AjaxLoadDetailsForAll(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxLoadDetailsForAll, self).get_context_data(count=Match.batch_process_matches(), **kwargs)


class AjaxGetMatchList(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxGetMatchList, self).get_context_data(matches=Match.get_all_limited(), **kwargs)


class AjaxLoadStaticDataView(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxLoadStaticDataView, self).get_context_data(heroes=Hero.load_heroes_from_api(),
                                                                    items=Item.load_items_from_api(), **kwargs)


class AjaxGetMatchCount(JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxGetMatchCount, self).get_context_data(matches=Match.get_count(),
                                                               unprocessed=Match.get_count_unprocessed(), **kwargs)


class HeroDetailView(DetailView):
    template_name = 'DotaStats/hero.html'
    model = Hero
    context_object_name = 'hero'

    def get_context_data(self, **kwargs):
        context = super(HeroDetailView, self).get_context_data(**kwargs)
        context['matches'] = PlayerInMatch.get_player_in_match_for_hero_id(self.object).order_by('-match_id')[:50]
        return context


class MatchDetailView(DetailView):
    template_name = 'DotaStats/match.html'
    model = Match
    context_object_name = 'match'

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        data, v = self.object.get_data_array()
        context['data'] = np.array_str(data)
        return context


class BuildDataView(View):

    @staticmethod
    def get(request):
        model = ScikitModel.create_model()
        return http.HttpResponse(json.dumps({'task_id': model.task_id}))


class BuildAndTestView(TemplateView):
    template_name = 'DotaStats/build.html'

    def get_context_data(self, **kwargs):
        context = super(BuildAndTestView, self).get_context_data(**kwargs)
        context['count'], context['accuracy'] = DotaModel.build()
        return context


class HeroListView(ListView):
    template_name = 'DotaStats/herolist.html'
    context_object_name = 'heroes'

    def get_queryset(self):
        return Hero.objects.filter(hero_id__gt=0)


class ItemListView(ListView):
    template_name = 'DotaStats/itemlist.html'
    context_object_name = 'items'
    model = Item

    def get_queryset(self):
        return super(ItemListView, self).get_queryset().filter(item_id__gt=0)


class MatchListView(ListView):
    template_name = 'DotaStats/matchlist.html'
    context_object_name = 'matches'
    model = Match
    paginate_by = 50

    def get_queryset(self):
        return super(MatchListView, self).get_queryset().order_by('-match_id')


class CreatePredictionView(CreateView):
    template_name = 'DotaStats/predict.html'
    form_class = PredictionForm
    context_object_name = 'form'

    def get_success_url(self):
        self.object.get_prediction()
        return reverse('index')

    def get_context_data(self, **kwargs):
        context = super(CreatePredictionView, self).get_context_data(**kwargs)
        context['predictions'] = MatchPrediction.objects.all()
        return context


class LogInView(FormView):
    template_name = 'DotaStats/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        form.clean()
        user = form.get_user()
        if user is not None:
            login(self.request, user)
        return super(LogInView, self).form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url is not None:
            return next_url
        else:
            return reverse('index')

    def get_context_data(self, **kwargs):
        context = super(LogInView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', None)
        return context


class LogOutView(View):

    def get(self, request):
        logout(request)
        return redirect(reverse('index'))