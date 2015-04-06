from __future__ import absolute_import

from django.db import models
import json
import urllib2
import datetime
import pytz
import numpy

from website.settings import DotaAPIKey
from djcelery.picklefield import PickledObjectField
from djcelery.models import TaskMeta

api_base = 'https://api.steampowered.com'
match_history = '/IDOTA2Match_570/GetMatchHistory/V001/'
details = '/IDOTA2Match_570/GetMatchDetails/V001/?match_id={0}&key={1}'
heroes = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v001/?key='
items = 'https://api.steampowered.com/IEconDOTA2_570/GetGameItems/v0001/?key='


class Player(models.Model):
    name = models.CharField(max_length=255)
    account_id = models.BigIntegerField(primary_key=True, default=0)


class Hero(models.Model):
    name = models.CharField(max_length=255)
    hero_id = models.IntegerField(primary_key=True, default=0)

    @staticmethod
    def load_heroes_from_api():
        url = heroes + DotaAPIKey
        try:
            data = json.load(urllib2.urlopen(url))
            print(json.dumps(data))
            result = 0
            if data['result']['status'] == 200:
                result = len(data['result']['heroes'])
                for new_hero in data['result']['heroes']:
                    hero, created = Hero.objects.get_or_create(hero_id=new_hero['id'])
                    hero.name = new_hero['name']
                    hero.save()
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    def get_winrate(self):
        player_in_match = PlayerInMatch.objects.filter(hero=self)
        if player_in_match.count() > 0:
            radiant = player_in_match.filter(player_slot__lt=128, match__radiant_win=True).count()
            dire = player_in_match.filter(player_slot__gt=127, match__radiant_win=True).count()
            return "%0.2f" % (float(radiant + dire) / float(player_in_match.count()))
        return 0


class Item(models.Model):
    name = models.CharField(max_length=255)
    item_id = models.IntegerField(primary_key=True, default=0)

    @staticmethod
    def load_items_from_api():
        url = items + DotaAPIKey
        try:
            data = json.load(urllib2.urlopen(url))
            result = 0
            print(json.dumps(data))
            if data['result']['status'] == 200:
                result = len(data['result']['items'])
                for new_item in data['result']['items']:
                    item, created = Item.objects.get_or_create(item_id=new_item['id'])
                    item.name = new_item['name']
                    item.save()
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)


# Game Modes
#     0 - None
#     1 - All Pick
#     2 - Captain's Mode
#     3 - Random Draft
#     4 - Single Draft
#     5 - All Random
#     6 - Intro
#     7 - Diretide
#     8 - Reverse Captain's Mode
#     9 - The Greeviling
#     10 - Tutorial
#     11 - Mid Only
#     12 - Least Played
#     13 - New Player Pool
#     14 - Compendium Matchmaking
#     16 - Captain's Draft
#
# Skill
#     0 - Any
#     1 - Normal
#     2 - High
#     3 - Very High

class Match(models.Model):
    match_id = models.IntegerField(primary_key=True, default=0)
    start_time = models.DateTimeField()
    match_seq_num = models.IntegerField()
    has_been_processed = models.BooleanField(default=False)
    radiant_win = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)
    tower_status_radiant = models.SmallIntegerField(default=0)
    tower_status_dire = models.SmallIntegerField(default=0)
    barracks_status_radiant = models.SmallIntegerField(default=0)
    barracks_status_dire = models.SmallIntegerField(default=0)
    cluster = models.IntegerField(default=0)
    first_blood_time = models.SmallIntegerField(default=0)
    lobby_type = models.SmallIntegerField(default=0)
    human_players = models.SmallIntegerField(default=0)
    league_id = models.SmallIntegerField(default=0)
    game_mode = models.SmallIntegerField(default=0)
    skill = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return str(self.match_id)

    def get_data_array(self):
        n_heroes = Hero.objects.all().count()
        heroes_in_match = self.playerinmatch_set.all()
        data = numpy.zeros((n_heroes * 2) + 2)
        for playerinmatch in heroes_in_match:
            hero_index = playerinmatch.hero_id
            if playerinmatch.player_slot > 127:
                hero_index += n_heroes
            data[hero_index] = 1
        return data, int(self.radiant_win)

    @staticmethod
    def get_all():
        return Match.objects.all()

    @staticmethod
    def get_match_api_url(game_mode=0, skill=0, date_min=0, date_max=0, min_players=10,
                          start_at_match_id=0, matches_requested=100):

        url = api_base + match_history + '?key=' + DotaAPIKey
        if game_mode > 0:
            url += '&game_mode=' + str(game_mode)
        if skill > 0:
            url += '&skill=' + str(skill)
        if date_min > 0:
            url += '&date_min=' + str(date_min)
        if date_max > 0:
            url += '&date_max=' + str(date_max)
        if min_players > 0:
            url += '&min_players=' + str(min_players)
        if start_at_match_id > 0:
            url += '&start_at_match_id=' + str(start_at_match_id)
        if matches_requested > 0:
            url += '&matches_requested=' + str(matches_requested)
        return url

    @staticmethod
    def batch_get_matches_from_api(n=500):
        last_match = 0
        counter = 0
        requested_matches = 100
        for i in range(0, n, requested_matches):
            url = Match.get_match_api_url(matches_requested=requested_matches, start_at_match_id=last_match)
            print url
            try:
                data = json.load(urllib2.urlopen(url))
                if data['result']['status'] == 1:
                    print data['result']['num_results']
                    for match in data['result']['matches']:
                        last_match = match['match_id']
                        start_time = datetime.datetime.fromtimestamp(match['start_time'])
                        new_match, created = Match.objects.get_or_create(match_id=match['match_id'],
                                                                         start_time=pytz.utc.localize(start_time),
                                                                         match_seq_num=match['match_seq_num'],
                                                                         lobby_type=match['lobby_type'])
                        new_match.save()
                        if created:
                            get_details.apply_async((new_match.match_id,), countdown=counter)
                            counter += 1
                    if data['result']['results_remaining'] < requested_matches:
                        break
                else:
                    return 'Status: {0}'.format(data['result']['status'])
            except urllib2.HTTPError as e:
                return 'HTTP error({0}): {1}'.format(e.errno, e.strerror)
        return 'Created: {0}'.format(counter)

    @staticmethod
    def get_new_matches_from_api():
        url = Match.get_match_api_url()
        try:
            data = json.load(urllib2.urlopen(url))
            counter = 0
            if data['result']['status'] == 1:
                for match in data['result']['matches']:
                    start_time = datetime.datetime.fromtimestamp(match['start_time'])
                    new_match, created = Match.objects.get_or_create(match_id=match['match_id'],
                                                                     start_time=pytz.utc.localize(start_time),
                                                                     match_seq_num=match['match_seq_num'],
                                                                     lobby_type=match['lobby_type'])
                    new_match.save()
                    if created:
                        get_details.apply_async((new_match.match_id,), countdown=counter)
                        counter += 1
            return counter
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    @staticmethod
    def get_winrate():
        return {'dire': Match.objects.filter(has_been_processed=True, radiant_win=False).count(),
                'radiant': Match.objects.filter(has_been_processed=True, radiant_win=True).count()}

    @staticmethod
    def get_unprocessed_match(n):
        unprocessed = Match.objects.filter(has_been_processed=False).order_by('match_id')
        return unprocessed[:n]

    @staticmethod
    def batch_process_matches():
        unprocessed = Match.objects.filter(has_been_processed=False).order_by('match_id')[:100]
        counter = 0
        for match in unprocessed:
            get_details.apply_async((match.match_id,), countdown=counter)
            counter += 1
        return unprocessed


    @staticmethod
    def get_count_unprocessed():
        return Match.objects.filter(has_been_processed=True).count()

    def load_details_from_api(self):
        url = api_base + details.format(self.match_id, DotaAPIKey)
        try:
            data = json.load(urllib2.urlopen(url))
            if data['result']:
                result = data['result']
                self.radiant_win = bool(result['radiant_win'])
                self.duration = int(result['duration'])
                self.tower_status_radiant = int(result['tower_status_radiant'])
                self.tower_status_dire = int(result['tower_status_dire'])
                self.barracks_status_radiant = int(result['barracks_status_radiant'])
                self.barracks_status_dire = int(result['barracks_status_dire'])
                self.cluster = int(result['cluster'])
                self.first_blood_time = int(result['first_blood_time'])
                self.lobby_type = int(result['lobby_type'])
                self.human_players = int(result['human_players'])
                for player_in_game in result['players']:
                    player_in_match = PlayerInMatch()
                    player_in_match.match_id = self.match_id
                    player_in_match.player, created = \
                        Player.objects.get_or_create(account_id=player_in_game['account_id'])
                    player_in_match.hero, created = Hero.objects.get_or_create(hero_id=player_in_game['hero_id'])
                    player_in_match.item_0, created = Item.objects.get_or_create(item_id=player_in_game["item_0"])
                    player_in_match.item_1, created = Item.objects.get_or_create(item_id=player_in_game["item_1"])
                    player_in_match.item_2, created = Item.objects.get_or_create(item_id=player_in_game["item_2"])
                    player_in_match.item_3, created = Item.objects.get_or_create(item_id=player_in_game["item_3"])
                    player_in_match.item_4, created = Item.objects.get_or_create(item_id=player_in_game["item_4"])
                    player_in_match.item_5, created = Item.objects.get_or_create(item_id=player_in_game["item_5"])
                    player_in_match.player_slot = player_in_game['player_slot']
                    player_in_match.kills = player_in_game['kills']
                    player_in_match.deaths = player_in_game['deaths']
                    player_in_match.assists = player_in_game['assists']
                    player_in_match.leaver_status = player_in_game['leaver_status']
                    player_in_match.gold = player_in_game['gold']
                    player_in_match.last_hits = player_in_game['last_hits']
                    player_in_match.denies = player_in_game['denies']
                    player_in_match.gold_per_min = player_in_game['gold_per_min']
                    player_in_match.xp_per_min = player_in_game['xp_per_min']
                    player_in_match.gold_spent = player_in_game['gold_spent']
                    player_in_match.hero_damage = player_in_game['hero_damage']
                    player_in_match.tower_damage = player_in_game['tower_damage']
                    player_in_match.hero_healing = player_in_game['hero_healing']
                    player_in_match.level = player_in_game['level']
                    player_in_match.save()
                self.has_been_processed = True
                self.save()
            return data
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    @staticmethod
    def get_matches_for_hero_id(hero_id):
        return Match.objects.filter(playerinmatch__hero__pk=hero_id)


class PlayerInMatch(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    player_slot = models.SmallIntegerField()
    hero = models.ForeignKey(Hero)
    item_0 = models.ForeignKey(Item, related_name="item_0")
    item_1 = models.ForeignKey(Item, related_name="item_1")
    item_2 = models.ForeignKey(Item, related_name="item_2")
    item_3 = models.ForeignKey(Item, related_name="item_3")
    item_4 = models.ForeignKey(Item, related_name="item_4")
    item_5 = models.ForeignKey(Item, related_name="item_5")
    kills = models.SmallIntegerField()
    deaths = models.SmallIntegerField()
    assists = models.SmallIntegerField()
    leaver_status = models.SmallIntegerField()
    gold = models.SmallIntegerField()
    last_hits = models.SmallIntegerField()
    denies = models.SmallIntegerField()
    gold_per_min = models.SmallIntegerField()
    xp_per_min = models.SmallIntegerField()
    gold_spent = models.IntegerField()
    hero_damage = models.IntegerField()
    tower_damage = models.SmallIntegerField()
    hero_healing = models.SmallIntegerField()
    level = models.SmallIntegerField()

    @staticmethod
    def get_player_in_match_for_hero_id(hero):
        return PlayerInMatch.objects.filter(hero=hero)

    def team(self):
        return 'Radiant' if self.player_slot <= 127 else 'Dire'


class ScikitModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    picked_model = PickledObjectField(
        compress=True, null=True, default=None, editable=False,
    )
    algorithm = models.CharField(max_length=255, null=True)
    min_date = models.DateTimeField(null=True)
    max_date = models.DateTimeField(null=True)
    match_count = models.IntegerField(default=0)
    task_id = models.CharField(max_length=255, null=True)
    is_ready = models.BooleanField(default=False)

    @staticmethod
    def create_model():
        model = ScikitModel()
        model.save()
        async_result = build_model.apply_async((3000, model.id))
        model.task_id = async_result.id
        model.save()
        return model


class MatchPrediction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(ScikitModel)
    predicted_radiant_win = models.NullBooleanField(null=True)

    @staticmethod
    def create_prediction(radiant_heroes, dire_heroes):
        prediction = MatchPrediction()
        for hero in radiant_heroes:
            hero_in_prediction = HeroInPrediction()
            hero_in_prediction.hero = hero
            hero_in_prediction.player_on_radiant = True
            hero_in_prediction.save()

        for hero in dire_heroes:
            hero_in_prediction = HeroInPrediction()
            hero_in_prediction.hero = hero
            hero_in_prediction.player_on_radiant = True
            hero_in_prediction.save()

        prediction.save()
        return prediction

    def get_data_array(self):
        n_heroes = Hero.objects.all().count()
        heroes_in_match = self.heroinprediction_set.all()
        data = numpy.zeros((n_heroes * 2) + 2)
        for hero_in_match in heroes_in_match:
            hero_index = hero_in_match.hero_id
            if not hero_in_match.player_on_radiant:
                hero_index += n_heroes
            data[hero_index] = 1
        return data


class HeroInPrediction(models.Model):
    match_prediction = models.ForeignKey(MatchPrediction)
    hero = models.ForeignKey(Hero)
    player_on_radiant = models.BooleanField(null=False, default=True)


#important: has to be last for circular import crap
from .tasks import get_details, build_model
