import mock
import os
import json
from random import randint

from requests.models import Response
import factory
from faker import Factory as FakerFactory
from django.test import TestCase, TransactionTestCase

from DotaStats.dota import DotaApi
from DotaStats.models import Hero, Item, Match

# run celery task synchronous
from django.conf import settings

settings.CELERY_ALWAYS_EAGER = True

fake = FakerFactory.create()


class HeroFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda o: fake.name().lower())
    localized_name = factory.LazyAttribute(lambda o: fake.name())
    hero_id = factory.Sequence(lambda n: n)
    primary_attribute = randint(0, 3)

    class Meta:
        model = Hero


class APITestAssetLoading(TestCase):
    def setUp(self):
        super(APITestAssetLoading, self).setUp()

    def test_hero_load(self):
        hero_data = []
        n_heroes = 10

        for i in range(0, n_heroes):
            hero_data.append({
                "name": fake.name().lower(),
                "id": i,
                "localized_name": fake.name()
            })

        data = {
            "result": {
                "heroes": hero_data,
                "status": 200,
                "count": 110
            }
        }

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        with mock.patch('requests.get', mocked_get):
            DotaApi.load_heroes_from_api()

        self.assertGreaterEqual(Hero.objects.all().count(), n_heroes)

    def test_item_load(self):
        item_data = []
        n_items = 10

        for i in range(0, n_items):
            item_data.append({
                "id": i,
                "name": fake.name().lower(),
                "cost": randint(0, 3000),
                "secret_shop": randint(0, 1),
                "side_shop": randint(0, 1),
                "recipe": randint(0, 1),
                "localized_name": fake.name()
            })

        data = {
            "result": {
                "items": item_data,
                "status": 200,
            }
        }

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        with mock.patch('requests.get', mocked_get):
            DotaApi.load_items_from_api()

        self.assertGreaterEqual(Item.objects.all().count(), n_items)

    def test_hero_attribute_load(self):
        data = {}
        n_heroes = 10

        for i in range(0, n_heroes):
            hero = HeroFactory()
            data[i] = {"Name": hero.localized_name, 'PrimaryStat': hero.primary_attribute}

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        with mock.patch('requests.get', mocked_get):
            count = DotaApi.load_hero_attribute_from_api()

        self.assertGreaterEqual(count, n_heroes)


class APITestMatchLoading(TransactionTestCase):
    def setUp(self):
        super(APITestMatchLoading, self).setUp()
        DotaApi.load_heroes_from_api()
        DotaApi.load_items_from_api()

    def test_load_matches(self):
        created = DotaApi.get_new_matches_by_sequence_from_api(max_requests=1)
        self.assertEqual(created, Match.objects.all().count())
