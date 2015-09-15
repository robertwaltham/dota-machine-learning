import time, datetime
from random import randint, getrandbits

import factory
from faker import Factory as FakerFactory
from django.test import TestCase

from DotaStats.models import Hero, Item, Player, Match, PlayerInMatch


# run celery task synchronous
from django.conf import settings

settings.CELERY_ALWAYS_EAGER = True

fake = FakerFactory.create()


class HeroFactory(factory.DjangoModelFactory):
    class Meta:
        model = Hero

    name = factory.LazyAttribute(lambda o: fake.name().lower())
    localized_name = factory.LazyAttribute(lambda o: fake.name())
    hero_id = factory.Sequence(lambda n: n + 1)
    primary_attribute = randint(0, 3)


class ItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.LazyAttribute(lambda o: fake.name().lower())
    localized_name = factory.LazyAttribute(lambda o: fake.name())
    item_id = factory.Sequence(lambda n: n + 1)


class PlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Player

    name = factory.LazyAttribute(lambda o: fake.name().lower())
    account_id = factory.Sequence(lambda n: n)


class PlayerInMatchFactory(factory.DjangoModelFactory):
    class Meta:
        model = PlayerInMatch

    player_slot = factory.Sequence(lambda n: n if n < 5 else n + 123)

    @factory.iterator
    def hero():
        for hero in Hero.objects.all():
            yield hero

    @factory.iterator
    def player():
        for player in Player.objects.all():
            yield player

    @factory.iterator
    def item_0():
        for item in Item.objects.all():
            yield item

    @factory.iterator
    def item_1():
        for item in Item.objects.all():
            yield item

    @factory.iterator
    def item_2():
        for item in Item.objects.all():
            yield item

    @factory.iterator
    def item_3():
        for item in Item.objects.all():
            yield item

    @factory.iterator
    def item_4():
        for item in Item.objects.all():
            yield item

    @factory.iterator
    def item_5():
        for item in Item.objects.all():
            yield item

    kills = randint(0, 100)
    deaths = randint(0, 100)
    assists = randint(0, 100)
    leaver_status = 0
    gold = randint(0, 100)
    last_hits = randint(0, 100)
    denies = randint(0, 100)
    gold_per_min = randint(0, 100)
    xp_per_min = randint(0, 100)
    gold_spent = randint(0, 100)
    hero_damage = randint(0, 100)
    tower_damage = randint(0, 100)
    hero_healing = randint(0, 100)
    level = randint(0, 100)


class MatchFactory(factory.DjangoModelFactory):
    class Meta:
        model = Match

    match_id = factory.Sequence(lambda n: n + 1)
    start_time = datetime.datetime.now()
    match_seq_num = factory.Sequence(lambda n: n + 1)
    has_been_processed = True
    radiant_win = bool(getrandbits(1))
    duration = randint(0, 1000)
    tower_status_radiant = int(getrandbits(4))
    tower_status_dire = int(getrandbits(4))
    barracks_status_radiant = int(getrandbits(4))
    barracks_status_dire = int(getrandbits(4))
    cluster = 0
    first_blood_time = randint(0, 1000)
    lobby_type = 0
    human_players = 10
    league_id = 0
    game_mode = 0
    skill = 0
    valid_for_model = True

    playerinmatch0 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=0)
    playerinmatch1 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=1)
    playerinmatch2 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=2)
    playerinmatch3 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=3)
    playerinmatch4 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=4)
    playerinmatch5 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=5)
    playerinmatch6 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=6)
    playerinmatch7 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=7)
    playerinmatch8 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=8)
    playerinmatch9 = factory.RelatedFactory(PlayerInMatchFactory, 'match', __sequence=9)


class TestHeroModel(TestCase):
    def setUp(self):
        self.hero = HeroFactory()

    def test_get_image(self):
        image2 = self.hero.get_image()
        self.assertEqual(image2, settings.STATIC_URL + 'image/heroes/' + self.hero.name[14:] + '.png')

    def test_get_small_image(self):
        image2 = self.hero.get_small_image()
        self.assertEqual(image2, settings.STATIC_URL + 'image/small_heroes/' + self.hero.name[14:] + '.png')


class TestItemModel(TestCase):
    def setUp(self):
        self.item = ItemFactory()

    def test_get_image(self):
        image2 = self.item.get_image()
        self.assertEqual(image2, settings.STATIC_URL + 'image/items/' + self.item.name[5:] + '.png')

    def test_get_small_image(self):
        image2 = self.item.get_small_image()
        self.assertEqual(image2, settings.STATIC_URL + 'image/small_items/' + self.item.name[5:] + '.png')


class TestMatchModel(TestCase):
    def setUp(self):
        PlayerFactory.reset_sequence()
        HeroFactory.reset_sequence()
        ItemFactory.reset_sequence()
        MatchFactory.reset_sequence()

        self.players = [PlayerFactory() for i in range(0, 10)]
        self.heroes = [HeroFactory() for i in range(0, 10)]
        self.items = [ItemFactory() for i in range(0, 10)]
        self.matches = [MatchFactory() for i in range(0, 5)]

    def test_get_matches_for_hero_id(self):
        hero_id = self.heroes[0].hero_id
        matches = Match.get_matches_for_hero_id(hero_id)
        # each hero appears in the match test data exactly once
        self.assertEqual(len(matches), len(self.matches))

    def test_get_matches_for_item_id(self):
        item_id = self.items[0].item_id
        matches = Match.get_matches_for_item_id(item_id)
        # each item appears in each match
        self.assertEqual(len(matches), len(self.matches))

    def test_get_count_by_date_set(self):
        count = Match.get_count_by_date_set()[0]
        self.assertEqual(count['date'], datetime.date.today())
        self.assertEqual(count['count'], len(self.matches))

    def test_get_related_matches(self):
        matches = self.matches[0].get_related_matches()
        self.assertEqual(len(matches), len(self.matches) - 1)
        for match in matches:
            self.assertEqual(match['count'], 10)
            self.assertTrue(match['match'] in self.matches)

    def process_match_info(self):
        slots = [0, 1, 2, 3, 4, 128, 129, 130, 131, 132]
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
        match = {
            "players": players,
            "radiant_win": False,
            "duration": randint(0, 1000),
            "start_time": time.time(),
            "match_id": 11,
            "match_seq_num": 11,
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
        }

        valid = Match.process_match_info(match)
        self.assertTrue(valid)
        self.assertIsInstance(Match.objects.get(match_id=11), Match)

