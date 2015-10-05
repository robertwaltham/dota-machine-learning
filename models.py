from __future__ import absolute_import, division
import json
import urllib2
import datetime
import pytz
import numpy
from itertools import groupby, imap

from bitstring import BitArray
from django.db import models, IntegrityError
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.core.serializers.json import DjangoJSONEncoder

from djcelery.picklefield import PickledObjectField


# Skill
#     0 - Any
#     1 - Normal
#     2 - High
#     3 - Very High

LEAVERS = {
    0: 'n/a',
    1: 'Disconnected',
    2: 'Disconnected Too Long',
    3: 'Abandoned',
    4: 'Afk',
    5: 'Never Connected',
    6: 'Never Connected Too Long',
}

LOBBIES = {
    -1: "Invalid",
    0: "Public Matchmaking",
    1: "Practice",
    2: "Tournament",
    3: "Tutorial",
    4: "Co-op with bots",
    5: "Team match",
    6: "Solo Queue",
    7: "Ranked",
    8: "Solo Mid 1vs1"
}

GAME_MODES = {
    0: "Unknown",
    1: "All Pick",
    2: "Captain's Mode",
    3: "Random Draft",
    4: "Single Draft",
    5: "All Random",
    6: "Intro",
    7: "Diretide",
    8: "Reverse Captain's Mode",
    9: "The Greeviling",
    10: "Tutorial",
    11: "Mid Only",
    12: "Least Played",
    13: "New Player Pool",
    14: "Compendium Matchmaking",
    16: "Captain's Draft"
}

valid_game_modes = [1, 2, 14, 16]


class Player(models.Model):
    name = models.CharField(max_length=255)
    account_id = models.BigIntegerField(primary_key=True, default=0)


class Hero(models.Model):
    name = models.CharField(max_length=255)
    localized_name = models.CharField(max_length=255, default='')
    hero_id = models.IntegerField(primary_key=True, default=0)
    PRIMARY_ATTRIBUTE = ((0, 'STR'), (1, 'AGI'), (2, 'INT'))
    primary_attribute = models.IntegerField(choices=PRIMARY_ATTRIBUTE, default=0)

    def get_image(self):
        if self.hero_id > 0:
            return static('image/heroes/' + self.name[14:] + '.png')
        else:
            return static('image/heroes/0.png')

    def get_small_image(self):
        if self.hero_id > 0:
            return static('image/small_heroes/' + self.name[14:] + '.png')
        else:
            return static('image/heroes/0.png')

    def __unicode__(self):
        return self.localized_name


class Item(models.Model):
    name = models.CharField(max_length=255)
    localized_name = models.CharField(max_length=255, default='')
    item_id = models.IntegerField(primary_key=True, default=0)
    recipe = models.BooleanField(default=False)
    cost = models.IntegerField(default=0)
    secret_shop = models.BooleanField(default=False)
    side_shop = models.BooleanField(default=False)

    def get_image(self):
        return static('image/items/' + self.name[5:] + '.png')

    def get_small_image(self):
        return static('image/small_items/' + self.name[5:] + '.png')

    def __unicode__(self):
        return self.localized_name


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
    valid_for_model = models.BooleanField(default=False)
    data = PickledObjectField(
        compress=False, null=True, default=None, editable=False,
    )

    @staticmethod
    def get_matches_for_hero_id(hero_id):
        return Match.objects.filter(playerinmatch__hero__pk=hero_id, valid_for_model=True).order_by('-match_id')[:10] \
            .prefetch_related('playerinmatch',
                              'playerinmatch__hero',
                              'playerinmatch__hero',
                              'playerinmatch__item_0',
                              'playerinmatch__item_1',
                              'playerinmatch__item_2',
                              'playerinmatch__item_3',
                              'playerinmatch__item_4',
                              'playerinmatch__item_5')

    @staticmethod
    def get_matches_for_item_id(item_id):
        item_filter = (Q(playerinmatch__item_0__pk=item_id) | Q(playerinmatch__item_1__pk=item_id) |
                       Q(playerinmatch__item_2__pk=item_id) | Q(playerinmatch__item_3__pk=item_id) |
                       Q(playerinmatch__item_4__pk=item_id) | Q(playerinmatch__item_5__pk=item_id)) & Q(
            valid_for_model=True)

        objects = Match.objects.filter(item_filter).distinct().order_by('-match_id')[:10].prefetch_related(
            'playerinmatch',
            'playerinmatch__hero',
            'playerinmatch__hero',
            'playerinmatch__item_0',
            'playerinmatch__item_1',
            'playerinmatch__item_2',
            'playerinmatch__item_3',
            'playerinmatch__item_4',
            'playerinmatch__item_5')

        return objects

    @staticmethod
    def process_match_info(match):
        valid_match = True
        start_time = datetime.datetime.fromtimestamp(match['start_time'])
        new_match, created = Match.objects.get_or_create(
            match_id=match['match_id'],
            start_time=pytz.utc.localize(start_time),
            match_seq_num=int(match['match_seq_num']),
            lobby_type=int(match['lobby_type']),
            radiant_win=bool(match['radiant_win']),
            tower_status_radiant=int(match['tower_status_radiant']),
            tower_status_dire=int(match['tower_status_dire']),
            barracks_status_radiant=int(match['barracks_status_radiant']),
            barracks_status_dire=int(match['barracks_status_dire']),
            cluster=int(match['cluster']),
            first_blood_time=int(match['first_blood_time']),
            human_players=int(match['human_players']),
            league_id=int(match['leagueid']),
            game_mode=int(match['game_mode']),
            duration=int(match['duration']),
            has_been_processed=True)

        if new_match.game_mode not in valid_game_modes:
            valid_match = False

        for player_in_game in match['players']:
            if 'account_id' in player_in_game:
                accountid = int(player_in_game['account_id'])
            else:
                # id for anon players
                accountid = 4294967295

            if 'leaver_status' in player_in_game:
                leaver_status = int(player_in_game['leaver_status'])
            else:
                leaver_status = 0

            if leaver_status > 0:
                valid_match = False

            player, created = \
                Player.objects.get_or_create(account_id=accountid)
            try:
                PlayerInMatch.objects.create(
                    match_id=match['match_id'],
                    player_slot=player_in_game['player_slot'],
                    hero_id=player_in_game['hero_id'],
                    item_0_id=player_in_game["item_0"],
                    item_1_id=player_in_game["item_1"],
                    item_2_id=player_in_game["item_2"],
                    item_3_id=player_in_game["item_3"],
                    item_4_id=player_in_game["item_4"],
                    item_5_id=player_in_game["item_5"],
                    kills=player_in_game['kills'],
                    deaths=player_in_game['deaths'],
                    assists=player_in_game['assists'],
                    leaver_status=leaver_status,
                    gold=player_in_game['gold'],
                    last_hits=player_in_game['last_hits'],
                    denies=player_in_game['denies'],
                    gold_per_min=player_in_game['gold_per_min'],
                    xp_per_min=player_in_game['xp_per_min'],
                    gold_spent=player_in_game['gold_spent'],
                    hero_damage=player_in_game['hero_damage'],
                    tower_damage=player_in_game['tower_damage'],
                    hero_healing=player_in_game['hero_healing'],
                    level=player_in_game['level'],
                    player=player)
            except KeyError as e:
                print e
            except IntegrityError as e:
                pass
        new_match.valid_for_model = valid_match
        new_match.save()
        return valid_match

    @staticmethod
    def get_count_by_date_set():
        return Match.objects.filter(valid_for_model=True) \
            .extra({'date': "date(start_time)"}) \
            .values('date') \
            .annotate(count=Count('match_id'))

    @staticmethod
    def get_valid_matches(n_matches=1000, min_duration=600):
        return Match.objects.filter(has_been_processed=True,
                                    duration__gt=min_duration,
                                    valid_for_model=True) \
            .order_by('?')[:n_matches] \
            .prefetch_related('playerinmatch', 'playerinmatch__hero')

    def __unicode__(self):
        return str(self.match_id)

    def get_data_array(self, n_heroes=None):
        if not n_heroes:
            #hero_id's aren't neccesarily sequential
            n_heroes = Hero.objects.all().aggregate(models.Max('hero_id'))
        heroes_in_match = self.playerinmatch.all()

        if len(heroes_in_match) < 10:
            return None, 0

        data = numpy.zeros((n_heroes * 2) + 2)
        for playerinmatch in heroes_in_match:
            hero_index = playerinmatch.hero_id
            if playerinmatch.player_slot > 127:
                hero_index += n_heroes
            data[hero_index - 1] = 1
        return data, int(self.radiant_win)

    def get_team_bitstring(self, n_heroes=None):

        heroes_in_match = self.playerinmatch.all()
        radiant = BitArray(length=128)
        dire = BitArray(length=128)

        for playerinmatch in heroes_in_match:
            hero_index = playerinmatch.hero_id
            if playerinmatch.player_slot > 127:
                dire[hero_index] = '0b1'
            else:
                radiant[hero_index] = '0b1'

        return radiant, dire

    def get_related_matches(self, n_matches=10000, n_heroes=None):
        if not n_heroes:
            n_heroes = Hero.objects.all().count()

        radiant, dire = self.get_team_bitstring(n_heroes)

        player_in_match_set = self.playerinmatch.all()

        query = Q(has_been_processed=True) & Q(valid_for_model=True)
        player_query = Q(playerinmatch__hero_id=player_in_match_set[0].hero_id)

        for player_in_match in player_in_match_set[1:]:
            player_query = player_query | Q(playerinmatch__hero_id=player_in_match.hero_id)

        matches = list(Match.objects
                       .filter(query, player_query)
                       .order_by('-match_id')
                       .distinct()[:n_matches]
                       .prefetch_related('playerinmatch', 'playerinmatch__hero'))

        result = []
        for match in matches:
            if match.match_id == self.match_id:
                continue

            test_radiant, test_dire = match.get_team_bitstring(n_heroes)

            count = (radiant & test_radiant).count(True) \
                    + (dire & test_dire).count(True)
            count2 = (radiant & test_dire).count(True) \
                     + (dire & test_radiant).count(True)

            if count > 3 or count2 > 3:
                result.append({'match': match, 'count': max(count, count2)})

        result.sort(key=lambda x: -1 * x['count'])
        return result

    def get_lobby_string(self):
        return LOBBIES[int(self.lobby_type)]


    def get_game_mode_string(self):
        try:
            return GAME_MODES[int(self.game_mode)]
        except KeyError as e:
            return "Unknown"


class PlayerInMatch(models.Model):
    match = models.ForeignKey(Match, related_name='playerinmatch')
    player = models.ForeignKey(Player)
    player_slot = models.SmallIntegerField()
    hero = models.ForeignKey(Hero, related_name='heroinmatch')
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

    class Meta:
        unique_together = (("match", "player_slot"),)

    def __unicode__(self):
        return 'Match: {0}, Hero: {1}, Team: {2}'.format(self.match_id, self.hero, self.team())

    def team(self):
        return 'Radiant' if self.player_slot <= 127 else 'Dire'

    def get_leaver_string(self):
        return leavers[int(self.leaver_status)]


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

    def __unicode__(self):
        return '{0} - {1} Count: {2}'.format(self.id, self.created, self.match_count)

    @staticmethod
    def create_model():
        from DotaStats.tasks import build_model
        model = ScikitModel()
        model.save()
        async_result = build_model.apply_async((3000, model.id))
        model.task_id = async_result.id
        model.save()
        return model

    @staticmethod
    def get_all_ready():
        return ScikitModel.objects.filter(is_ready=True).order_by('-created')


class MatchPrediction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(ScikitModel)
    predicted_radiant_win = models.NullBooleanField(null=True, default=None)
    radiant_player_0 = models.ForeignKey(Hero, related_name="radiant_player_0", null=True)
    radiant_player_1 = models.ForeignKey(Hero, related_name="radiant_player_1", null=True)
    radiant_player_2 = models.ForeignKey(Hero, related_name="radiant_player_2", null=True)
    radiant_player_3 = models.ForeignKey(Hero, related_name="radiant_player_3", null=True)
    radiant_player_4 = models.ForeignKey(Hero, related_name="radiant_player_4", null=True)
    radiant_player_5 = models.ForeignKey(Hero, related_name="radiant_player_5", null=True)
    dire_player_0 = models.ForeignKey(Hero, related_name="dire_player_0", null=True)
    dire_player_1 = models.ForeignKey(Hero, related_name="dire_player_1", null=True)
    dire_player_2 = models.ForeignKey(Hero, related_name="dire_player_2", null=True)
    dire_player_3 = models.ForeignKey(Hero, related_name="dire_player_3", null=True)
    dire_player_4 = models.ForeignKey(Hero, related_name="dire_player_4", null=True)
    dire_player_5 = models.ForeignKey(Hero, related_name="dire_player_5", null=True)

    def get_data_array(self):
        n_heroes = Hero.objects.all().count()
        data = numpy.zeros((n_heroes * 2) + 2)
        data[self.radiant_player_0.hero_id] = 1
        data[self.radiant_player_1.hero_id] = 1
        data[self.radiant_player_2.hero_id] = 1
        data[self.radiant_player_3.hero_id] = 1
        data[self.radiant_player_4.hero_id] = 1

        data[self.dire_player_0.hero_id + n_heroes] = 1
        data[self.dire_player_1.hero_id + n_heroes] = 1
        data[self.dire_player_2.hero_id + n_heroes] = 1
        data[self.dire_player_3.hero_id + n_heroes] = 1
        data[self.dire_player_4.hero_id + n_heroes] = 1
        return data

    def get_predicted_team(self):
        if self.predicted_radiant_win is None:
            return 'None'
        else:
            if self.predicted_radiant_win:
                return 'Radiant'
            else:
                return 'Dire'

    def get_prediction(self):
        prediction = DotaModel.predict(self.model_id, self.get_data_array())
        if prediction == 1:
            self.predicted_radiant_win = True
        else:
            self.predicted_radiant_win = False
        self.save()
        return prediction


# important: has to be last for circular import crap
from .scikit import DotaModel
