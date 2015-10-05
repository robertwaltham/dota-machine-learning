import json

from faker import Factory as FakerFactory
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import caches
from django.conf import settings
from rest_framework.reverse import reverse

from DotaStats.models import Hero, Item, Player, Match, PlayerInMatch
from DotaStats.tests.test_models import HeroFactory, ItemFactory, PlayerFactory, MatchFactory


# run celery task synchronous
settings.CELERY_ALWAYS_EAGER = True

fake = FakerFactory.create()


class TestDotaView(TestCase):
    def setUp(self):
        self.user_password = 'temporary'
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', self.user_password)
        PlayerFactory.reset_sequence()
        HeroFactory.reset_sequence()
        ItemFactory.reset_sequence()
        MatchFactory.reset_sequence()

        cache = caches['default']
        cache.clear()

        self.players = [PlayerFactory() for i in range(0, 10)]
        self.heroes = [HeroFactory() for i in range(0, 10)]
        self.items = [ItemFactory() for i in range(0, 10)]
        self.matches = [MatchFactory() for i in range(0, 5)]

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'DotaStats/index.html')
        self.assertEqual(response.cookies.items()[0][0], 'csrftoken')

    def test_log_in_view(self):
        response = self.client.post(reverse('login'),
                                    {'username': self.user.username,
                                     'password': self.user_password})
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_hero_recent_matches_set(self):
        match_id = self.matches[0].match_id
        response = self.client.get(reverse('herorecentmatches-list') + str(match_id) + '/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['matches']), 5)

    def test_item_recent_matches_set(self):
        item_id = self.items[0].item_id
        response = self.client.get(reverse('itemrecentmatches-list') + str(item_id) + '/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['matches']), 5)

    def test_match_view_set(self):
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 5)

    def test_item_view_set(self):
        response = self.client.get(reverse('item-list'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 10)

    def test_hero_view_set(self):
        response = self.client.get(reverse('hero-list'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 10)

    def test_match_date_count_set(self):
        response = self.client.get(reverse('matchcreatedbydate-list'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(int(response_data[0]['count']), 5)
