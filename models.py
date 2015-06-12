from __future__ import absolute_import
import json
import urllib2
import datetime
import pytz
import numpy
from itertools import groupby, imap

from django.db import models, IntegrityError
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

from website.settings import DotaAPIKey
from djcelery.picklefield import PickledObjectField

api_base = 'https://api.steampowered.com'
match_history = '/IDOTA2Match_570/GetMatchHistory/V001/'
match_history_sequence = '/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?key={0}&start_at_match_seq_num={1}'
details = '/IDOTA2Match_570/GetMatchDetails/V001/?match_id={0}&key={1}'
heroes_url = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v001/?key={0}&language={1}'
hero_stats_url = 'http://herostats.io:322/heroes/all'
items = 'https://api.steampowered.com/IEconDOTA2_570/GetGameItems/v0001/?key={0}&language={1}'
language = 'en_us'

# Skill
#     0 - Any
#     1 - Normal
#     2 - High
#     3 - Very High

leavers = {
    0: 'n/a',
    1: 'Disconnected',
    2: 'Disconnected Too Long',
    3: 'Abandoned',
    4: 'Afk',
    5: 'Never Connected',
    6: 'Never Connected Too Long',
}

lobbies = {
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

game_modes = {
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

    @staticmethod
    def load_heroes_from_api():
        url = heroes_url.format(DotaAPIKey, language)
        try:
            # load data from Dota 2 API
            data = json.load(urllib2.urlopen(url))
            result = 0
            if data['result']['status'] == 200:
                result = len(data['result']['heroes'])
                for new_hero in data['result']['heroes']:
                    hero, created = Hero.objects.get_or_create(hero_id=new_hero['id'])
                    hero.name = new_hero['name']
                    hero.localized_name = new_hero['localized_name']
                    hero.save()

            # load data from secondary API
            for key, hero_data in json.load(urllib2.urlopen(hero_stats_url)).iteritems():
                try:
                    hero = Hero.objects.get(localized_name=hero_data['Name'])
                    hero.primary_attribute = hero_data['PrimaryStat']
                    hero.save()
                except ObjectDoesNotExist as e:
                    print "ObjectDoesNotExist"
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    @staticmethod
    def get_heroes_by_attribute():
        return [list(g) for k, g in groupby(Hero.objects.all().order_by('primary_attribute'),
                                            lambda x: x.primary_attribute)]

    @staticmethod
    def get_serialized_hero_list():
        return json.dumps(
            [{'name': hero.name, 'localized_name': hero.localized_name, 'hero_id': hero.hero_id,
              'primary_attribute': hero.primary_attribute, 'image': hero.get_image()}
             for hero in Hero.objects.all().filter(hero_id__gt=0)])

    def get_winrate(self):
        player_in_match = PlayerInMatch.objects.filter(hero=self)
        if player_in_match.count() > 0:
            radiant = player_in_match.filter(player_slot__lt=128, match__radiant_win=True).count()
            dire = player_in_match.filter(player_slot__gt=127, match__radiant_win=True).count()
            return "%0.2f" % (float(radiant + dire) / float(player_in_match.count()))
        return 0

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

    @staticmethod
    def load_items_from_api():
        url = items.format(DotaAPIKey, language)
        try:
            data = json.load(urllib2.urlopen(url))
            result = 0
            if data['result']['status'] == 200:
                result = len(data['result']['items'])
                for new_item in data['result']['items']:
                    item, created = Item.objects.get_or_create(item_id=new_item['id'])
                    item.name = new_item['name']
                    item.recipe = bool(new_item['recipe'])
                    item.secret_shop = bool(new_item['secret_shop'])
                    item.side_shop = bool(new_item['side_shop'])
                    item.localized_name = new_item['localized_name']
                    item.cost = int(new_item['cost'])
                    item.save()
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

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
        return Match.objects.filter(playerinmatch__hero__pk=hero_id).order_by('-match_id').prefetch_related(
            'playerinmatch', 'playerinmatch__hero')[:50]

    @staticmethod
    def get_all():
        return Match.objects.all()

    @staticmethod
    def get_all_limited():
        return list(Match.objects.all().values('match_id', 'duration', 'radiant_win'))

    @staticmethod
    def get_match_api_url(game_mode=0, skill=0, date_min=0, date_max=0, min_players=10,
                          start_at_match_id=0, matches_requested=100):

        url = api_base + match_history + '?key=' + DotaAPIKey
        #api is bugged and doesn't honor game mode flag
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
    def batch_get_matches_from_api(n=10):
        from DotaStats.tasks import get_details
        last_match = 0
        counter = 0
        requested_matches = 500
        starting_match_id = 0
        match_ids = []
        for i in range(0, n, requested_matches):
            url = Match.get_match_api_url(game_mode=1, matches_requested=requested_matches,
                                          start_at_match_id=last_match)
            print url
            try:
                data = json.load(urllib2.urlopen(url))
                if data['result']['status'] == 1:
                    print data['result']['num_results']
                    if data['result']['num_results'] > 0 and starting_match_id == 0:
                        starting_match_id = data['result']['matches'][0]['match_id']
                    for match in data['result']['matches']:
                        last_match = match['match_id']
                        match_ids.append(last_match)
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
        from DotaStats.tasks import get_details
        url = Match.get_match_api_url(game_mode=1)
        print url
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
    def get_new_matches_by_sequence_from_api(match_seq_num=None):
        from DotaStats.tasks import process_match
        #get sequence number of latest match
        if not match_seq_num:
            latest_match_url = Match.get_match_api_url(matches_requested=1)
            try:
                latest_match_data = json.load(urllib2.urlopen(latest_match_url))
                if latest_match_data['result']['status'] == 1:
                    match_seq_num = latest_match_data['result']['matches'][0]['match_seq_num']
                else:
                    return "API Error {0}".format(latest_match_data['result']['status'])

            except urllib2.HTTPError as e:
                return "HTTP error({0}): {1}".format(e.errno, e.strerror)

        api_has_more_matches = True
        match_data = None
        n_matches_created = 0
        requests = 0
        #get matches until there are no new matches
        while api_has_more_matches:
            match_seq_url = api_base + match_history_sequence.format(DotaAPIKey, match_seq_num)
            try:
                match_data = json.load(urllib2.urlopen(match_seq_url))
            except urllib2.HTTPError as e:
                return "HTTP error({0}): {1}".format(e.errno, e.strerror)

            if match_data['result']['status'] == 1:
                if len(match_data['result']['matches']) == 0:
                    api_has_more_matches = False
                    break

                for match in match_data['result']['matches']:
                    process_match.apply_async((match,))
                    if int(match['match_seq_num']) > match_seq_num:
                        match_seq_num = int(match['match_seq_num'])
                    n_matches_created += 1
            else:
                return "API Error {0}".format(match_data['result']['status'])

            #sanity
            requests += 1
            if requests >= 5:
                break

        return "Created: {0} Requests: {1}".format(n_matches_created, requests)

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

        if not new_match.game_mode in valid_game_modes:
            valid_match = False

        for player_in_game in match['players']:
            if 'account_id' in player_in_game:
                accountid = int(player_in_game['account_id'])
            else:
                #id for anon players
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
        return created

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
        from DotaStats.tasks import get_details
        unprocessed = Match.objects.filter(has_been_processed=False).order_by('match_id')[:100]
        counter = 0
        for match in unprocessed:
            get_details.apply_async((match.match_id,), countdown=counter)
            counter += 1
        return unprocessed


    @staticmethod
    def get_count_unprocessed():
        return Match.objects.filter(has_been_processed=True).count()

    @staticmethod
    def get_count():
        return Match.objects.count()

    def get_details_url(self):
        return api_base + details.format(self.match_id, DotaAPIKey)

    def load_details_from_api(self):
        url = self.get_details_url()
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
                self.game_mode = int(result['game_mode'])
                for player_in_game in result['players']:
                    hero, created = Hero.objects.get_or_create(hero_id=player_in_game['hero_id'])
                    item_0, created = Item.objects.get_or_create(item_id=player_in_game["item_0"])
                    item_1, created = Item.objects.get_or_create(item_id=player_in_game["item_1"])
                    item_2, created = Item.objects.get_or_create(item_id=player_in_game["item_2"])
                    item_3, created = Item.objects.get_or_create(item_id=player_in_game["item_3"])
                    item_4, created = Item.objects.get_or_create(item_id=player_in_game["item_4"])
                    item_5, created = Item.objects.get_or_create(item_id=player_in_game["item_5"])
                    player, created = \
                        Player.objects.get_or_create(account_id=player_in_game['account_id'])

                    PlayerInMatch.objects.get_or_create(
                        match_id=self.match_id,
                        player_slot=player_in_game['player_slot'],
                        hero=hero,
                        item_0=item_0,
                        item_1=item_1,
                        item_2=item_2,
                        item_3=item_3,
                        item_4=item_4,
                        item_5=item_5,
                        kills=player_in_game['kills'],
                        deaths=player_in_game['deaths'],
                        assists=player_in_game['assists'],
                        leaver_status=player_in_game['leaver_status'],
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
                self.has_been_processed = True
                self.save()
            return data
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    def get_heroes_for_match(self):
        return Hero.objects.filter(heroinmatch__match__match_id=self.match_id)

    def __unicode__(self):
        return str(self.match_id)

    def get_data_array(self, n_heroes=None):
        if not n_heroes:
            n_heroes = Hero.objects.all().count()
        # if self.data is not None:
        #     return self.data, int(self.radiant_win)
        # else:
        heroes_in_match = self.playerinmatch.all()

        if len(heroes_in_match) < 10:
            return None, 0

        data = numpy.zeros((n_heroes * 2) + 2)
        for playerinmatch in heroes_in_match:
            hero_index = playerinmatch.hero_id
            if playerinmatch.player_slot > 127:
                hero_index += n_heroes
            data[hero_index] = 1
            # self.data = data
            # self.save()
        return data, int(self.radiant_win)

    def get_hero_ids_in_match(self):
        return self.playerinmatch_set.all().values('hero_id')

    def get_lobby_string(self):
        return lobbies[int(self.lobby_type)]

    def get_game_mode_string(self):
        try:
            return game_modes[int(self.game_mode)]
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

    @staticmethod
    def get_player_in_match_for_hero_id(hero):
        return PlayerInMatch.objects.filter(hero=hero)

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

#important: has to be last for circular import crap
from .scikit import DotaModel
