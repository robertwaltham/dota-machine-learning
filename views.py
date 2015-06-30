import json

from django.views.generic import DetailView, View, TemplateView, ListView, FormView
from django.views.generic.edit import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import http

from models import Match, Item, Hero, ScikitModel, MatchPrediction
from forms import PredictionForm, ModelTestForm
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
        context['count'] = Match.get_all().filter(valid_for_model=True).count()
        context['matches'] = []
        context['processed'] = Match.get_count_unprocessed()
        context['models'] = ScikitModel.objects.filter(is_ready=True).count()
        context['heroes'] = Hero.get_serialized_hero_list()
        context['date_count'] = Match.get_count_by_date()
        print context['date_count']
        return context


class AjaxLoadMatchesFromAPI(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxLoadMatchesFromAPI, self).get_context_data(
            status=Match.get_new_matches_by_sequence_from_api(), **kwargs)


class AjaxLoadDetailsForAll(LoginRequiredMixin, JSONView):

    def get_context_data(self, **kwargs):
        return super(AjaxLoadDetailsForAll, self).get_context_data(count=len(Match.batch_process_matches()), **kwargs)


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


class AjaxUpdateMatchDetails(SingleObjectMixin, JSONView, LoginRequiredMixin):
    model = Match
    context_object_name = 'match'
    object = None

    def get_context_data(self, **kwargs):
        match = self.get_object()
        match.load_details_from_api()
        return super(AjaxUpdateMatchDetails, self).get_context_data(
            heroes=list(match.get_heroes_for_match().values('hero_id', 'localized_name')),
            **kwargs)


class HeroDetailView(DetailView):
    template_name = 'DotaStats/hero.html'
    model = Hero
    context_object_name = 'hero'

    def get_queryset(self):
        return super(HeroDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        return super(HeroDetailView, self).get_context_data(
            matches=Match.get_matches_for_hero_id(self.object.hero_id), **kwargs)


class MatchDetailView(DetailView):
    template_name = 'DotaStats/match.html'
    model = Match
    context_object_name = 'match'

    def get_queryset(self):
        return super(MatchDetailView, self).get_queryset().prefetch_related('playerinmatch', 'playerinmatch__hero')

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data()
        context['related'] = self.object.get_related_matches()
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
        form = ModelTestForm(self.request.GET)
        context['form'] = form
        DotaModel.mapreduce()

        if form.is_valid():
            # data = form.cleaned_data
            # context['count'], context['accuracy'], context['radiant_win']\
            #     = DotaModel.build(data['n_matches'], data['n_tests'], data['min_duration'], data['algorithm'])
            context['valid'] = True
        else:
            context['valid'] = False
        return context


class HeroListView(ListView):
    template_name = 'DotaStats/herolist.html'
    context_object_name = 'heroes'

    def get_queryset(self):
        return Hero.objects.filter(hero_id__gt=0).order_by('primary_attribute')


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
        return super(MatchListView, self).get_queryset().filter(valid_for_model=True).order_by('-match_id')\
            .prefetch_related('playerinmatch', 'playerinmatch__hero')


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