import csv

from django.views.generic import View, TemplateView, ListView, FormView
from django.views.decorators.csrf import requires_csrf_token
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import models
from django import http
from django.http import JsonResponse
from django.core.cache import caches
from django.conf import settings

from rest_framework import viewsets, pagination
from djcelery.models import TaskMeta
from celery import states

from models import Match, Item, Hero
from serializers import HeroSerializer, MatchSerializer, ItemSerializer, HeroRecentMatchesSerializer, \
    MatchDateCountSerializer, ItemRecentMatchSerializer, TaskMetaSerializer


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


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class CSVView(TemplateView):
    """A view that streams a large CSV file."""

    def render_to_response(self, context, **response_kwargs):
        rows = self.get_rows()
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = http.StreamingHttpResponse((writer.writerow(row) for row in rows), content_type="text/csv")

        filename = getattr(self, 'file_name', 'data.csv')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
        return response


class IndexView(TemplateView):
    template_name = 'DotaStats/index.html'

    def get_context_data(self, **kwargs):

        self.request.META['CSRF_COOKIE_USED'] = True  # force csrf cookie
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            context['GA_KEY'] = settings.GA_KEY
        except AttributeError:
            pass
        return context

    @method_decorator(requires_csrf_token)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class MatchCSVView(CSVView):
    file_name = 'match_data.csv'

    def get_rows(self):
        matches = Match.get_valid_matches(n_matches=5000)
        heroes = Hero.objects.all().filter(hero_id__gt=0).order_by('hero_id')
        # hero_ids aren't neccessarily sequential
        n_heroes = heroes.aggregate(models.Max('hero_id'))['hero_id__max']

        radiant_heroes = [x for x in range(n_heroes)]
        for hero in heroes:
            radiant_heroes[hero.hero_id - 1] = 'radiant_' + hero.name + '_' + str(hero.hero_id)

        dire_heroes = [x for x in range(n_heroes)]
        for hero in heroes:
            dire_heroes[hero.hero_id - 1] = 'dire_' + hero.name + '_' + str(hero.hero_id)
        header = ['match_id', 'duration', 'radiant_win'] + radiant_heroes + dire_heroes

        rows = [header]
        for match in matches:
            array, win = match.get_data_array(n_heroes=n_heroes)
            row = [match.match_id, match.duration, win] + array.tolist()
            rows.append(row)
        return rows


class LogInView(FormView):
    template_name = 'DotaStats/login.html'
    form_class = AuthenticationForm

    def post(self, request, *args, **kwargs):
        return super(LogInView, self).post(self, request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.clean()
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            return JsonResponse({
                'user': user.username,
                'errors': False
            })
        else:
            return JsonResponse({
                'user': '',
                'errors': True
            })

    def form_invalid(self, form, **kwargs):
        super(LogInView, self).form_invalid(form)
        return JsonResponse({'user': False, 'errors': form.errors}, status=400)


class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('index'))


class CachedAPIViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cache = caches['default']
        cache_key = getattr(self, 'cache_key', None)
        cache_timeout = getattr(self, 'cache_timeout', 300)

        if cache_key is None:
            raise NotImplementedError('cache_key is required')

        cached_response = cache.get(cache_key)

        if cached_response is not None:
            return http.HttpResponse(cached_response, status=200)

        response = super(CachedAPIViewMixin, self).dispatch(request, *args, **kwargs)
        response.render()
        cache.set(cache_key, response.content, timeout=cache_timeout)

        return response


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 25


class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all().filter(hero_id__gt=0)
    serializer_class = HeroSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().filter(item_id__gt=0, recipe=False).order_by('item_id')
    serializer_class = ItemSerializer


class HeroRecentMatchesSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all().filter(hero_id__gt=0)
    serializer_class = HeroRecentMatchesSerializer


class ItemRecentMatchSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().filter(item_id__gt=0)
    serializer_class = ItemRecentMatchSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all().filter(valid_for_model=True).order_by('-match_id') \
        .prefetch_related('playerinmatch',
                          'playerinmatch__hero',
                          'playerinmatch__item_0',
                          'playerinmatch__item_1',
                          'playerinmatch__item_2',
                          'playerinmatch__item_3',
                          'playerinmatch__item_4',
                          'playerinmatch__item_5')
    serializer_class = MatchSerializer
    pagination_class = StandardResultsSetPagination


class MatchDateCountSet(CachedAPIViewMixin, viewsets.ModelViewSet):
    cache_key = 'match_date_count'
    cache_timeout = 300
    queryset = Match.get_count_by_date_set()
    serializer_class = MatchDateCountSerializer


class TaskMetaSet(viewsets.ModelViewSet):
    serializer_class = TaskMetaSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        if status is not None and status in states.ALL_STATES:
            return TaskMeta.objects.all().order_by('-id').filter(status=status)[:100]
        else:
            return TaskMeta.objects.all().order_by('-id')[:100]
