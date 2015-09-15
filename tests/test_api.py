import mock, time
from random import randint

from requests.models import Response
import factory
from faker import Factory as FakerFactory
from django.test import TestCase, TransactionTestCase

from DotaStats.dota import DotaApi
from DotaStats.models import Hero, Item, Player, Match

from DotaStats.tests.test_models import HeroFactory, ItemFactory, PlayerFactory

# run celery task synchronous
from django.conf import settings

settings.CELERY_ALWAYS_EAGER = True

fake = FakerFactory.create()


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
        PlayerFactory.reset_sequence()
        HeroFactory.reset_sequence()
        ItemFactory.reset_sequence()
        self.items = [ItemFactory() for i in range(0, 10)]
        self.players = [PlayerFactory() for i in range(0, 10)]
        self.heroes = [HeroFactory() for i in range(0, 10)]

    def test_load_matches(self):
        data = {
            "result": {
                "status": 1,
                "num_results": 1,
                "total_results": 500,
                "results_remaining": 499,
                "matches": [
                    {
                        "match_id": randint(0, 10000),
                        "match_seq_num": randint(0, 10000),
                    }
                ]
            }
        }

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        mocked_api_request = mock.MagicMock(return_value=False)

        with mock.patch('requests.get', mocked_get):
            with mock.patch('DotaStats.dota.DotaApi.load_matches_from_api_by_sequence_number', mocked_api_request):
                created = DotaApi.load_matches_from_api()

    def test_load_matches_by_sequence_empty_matches(self):
        data = {
            "result": {
                "status": 1,
                "matches": []
            }
        }

        match_sequence_number = randint(0, 1000)

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        with mock.patch('requests.get', mocked_get):
            response = DotaApi.load_matches_from_api_by_sequence_number(match_sequence_number=match_sequence_number)
            self.assertGreaterEqual(response, False)

    def test_load_matches_by_sequence(self):
        slots = [0, 1, 2, 3, 4, 128, 129, 130, 131, 132]
        matches = []
        for i in range(0, 10):
            players = []
            for j in range(0, 10):
                players.append({
                    "account_id": self.players[j].account_id,
                    "player_slot": slots[j],
                    "hero_id": self.heroes[j].hero_id,
                    "item_0": self.items[randint(0, 9)].item_id,
                    "item_1": self.items[randint(0, 9)].item_id,
                    "item_2": self.items[randint(0, 9)].item_id,
                    "item_3": self.items[randint(0, 9)].item_id,
                    "item_4": self.items[randint(0, 9)].item_id,
                    "item_5": self.items[randint(0, 9)].item_id,
                    "kills": randint(0, 9),
                    "deaths": randint(0, 9),
                    "assists": randint(0, 9),
                    "leaver_status": 0,
                    "gold": randint(0, 1000),
                    "last_hits": randint(0, 100),
                    "denies": randint(0, 10),
                    "gold_per_min": randint(0, 700),
                    "xp_per_min": randint(0, 700),
                    "gold_spent": randint(0, 10000),
                    "hero_damage": randint(0, 900),
                    "tower_damage": randint(0, 900),
                    "hero_healing": randint(0, 900),
                    "level": randint(0, 25)
                })
            matches.append({
                "players": players,
                "radiant_win": False,
                "duration": randint(0, 1000),
                "start_time": time.time(),
                "match_id": i,
                "match_seq_num": i,
                "tower_status_radiant": randint(0, 128),
                "tower_status_dire": randint(0, 128),
                "barracks_status_radiant": randint(0, 128),
                "barracks_status_dire": randint(0, 128),
                "cluster": 0,
                "first_blood_time": randint(0, 128),
                "lobby_type": 0,
                "human_players": 10,
                "leagueid": 0,
                "positive_votes": 0,
                "negative_votes": 0,
                "game_mode": 0,
                "engine": 0
            })

        data = {
            "result": {
                "status": 1,
                "matches": matches
            }
        }

        match_sequence_number = randint(0, 1000)

        response = Response()
        response.status_code = 200
        response.json = mock.MagicMock(return_value=data)
        mocked_get = mock.MagicMock(return_value=response)

        with mock.patch('requests.get', mocked_get):
            response = DotaApi.load_matches_from_api_by_sequence_number(match_sequence_number=match_sequence_number)
            self.assertGreaterEqual(Match.objects.all().count(), 10)
