from django.test import TestCase, TransactionTestCase
from django.db import transaction

from DotaStats.dota import DotaApi
from DotaStats.models import Hero, Item, Match

# run celery task synchronous
from django.conf import settings
settings.CELERY_ALWAYS_EAGER = True


class APITestAssetLoading(TestCase):
    def setUp(self):
        pass

    def test_hero_load(self):
        DotaApi.load_heroes_from_api()
        # 110 heros loaded
        self.assertGreaterEqual(Hero.objects.all().count(), 110)

    def test_item_load(self):
        DotaApi.load_items_from_api()
        # 257 items loaded
        self.assertGreaterEqual(Item.objects.all().count(), 257)


class APITestMatchLoading(TransactionTestCase):
    def setUp(self):
        DotaApi.load_heroes_from_api()
        DotaApi.load_items_from_api()

    def test_load_matches(self):
        created = DotaApi.get_new_matches_by_sequence_from_api(max_requests=1)
        self.assertEqual(created, Match.objects.all().count())

    def test_load_matches_fixed_sequence_number(self):
        created = DotaApi.get_new_matches_by_sequence_from_api(match_seq_num=1, max_requests=1)
        self.assertEqual(created, Match.objects.all().count())

    def test_load_matches_multiple_requests(self):
        created = DotaApi.get_new_matches_by_sequence_from_api(max_requests=2)
        self.assertEqual(created, Match.objects.all().count())
