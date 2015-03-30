from django.db import models
import json
import urllib2
import datetime


key = '8F60050E57157048213A74F8D0F08EFA'
api_base = 'https://api.steampowered.com'
match_history = '/IDOTA2Match_570/GetMatchHistory/V001/?min_players=10&matches_requested=25&key='
details = '/IDOTA2Match_570/GetMatchDetails/V001/?match_id={0}&key={1}'
heroes = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v001/?key='
items = 'https://api.steampowered.com/IEconDOTA2_570/GetGameItems/v0001/?key='


class Player(models.Model):
    name = models.CharField(max_length=255)
    account_id = models.IntegerField(primary_key=True, default=0)


class Hero(models.Model):
    name = models.CharField(max_length=255)
    hero_id = models.IntegerField(primary_key=True, default=0)

    @staticmethod
    def load_heroes_from_api():
        url = heroes + key
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
            return (radiant + dire) / player_in_match.count()
        return 0


class Item(models.Model):
    name = models.CharField(max_length=255)
    item_id = models.IntegerField(primary_key=True, default=0)

    @staticmethod
    def load_items_from_api():
        url = items + key
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

    def __unicode__(self):
        return str(self.match_id)

    @staticmethod
    def get_all():
        return Match.objects.all()

    @staticmethod
    def get_new_matches_from_api():
        url = api_base + match_history + key
        try:
            data = json.load(urllib2.urlopen(url))
            result = []
            if data['result']['status'] == 1:
                for match in data['result']['matches']:
                    start_time = datetime.datetime.fromtimestamp(match['start_time'])
                    new_match = Match()
                    new_match.match_id = match['match_id']
                    new_match.match_seq_num = match['match_seq_num']
                    new_match.start_time = start_time
                    new_match.lobby_type = match['lobby_type']
                    new_match.save()
                    result.append(new_match)
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    @staticmethod
    def get_winrate():
        return {'dire': Match.objects.filter(has_been_processed=True, radiant_win=False).count(),
                'radiant': Match.objects.filter(has_been_processed=True, radiant_win=True).count()}

    @staticmethod
    def get_unprocessed_match():
        unprocessed = Match.objects.filter(has_been_processed=False).order_by('match_id')
        return unprocessed[0]

    @staticmethod
    def get_count_unprocessed():
        return Match.objects.filter(has_been_processed=True).count()

    def load_details_from_api(self):
        url = api_base + details.format(self.match_id, key)
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
    gold_spent = models.SmallIntegerField()
    hero_damage = models.SmallIntegerField()
    tower_damage = models.SmallIntegerField()
    hero_healing = models.SmallIntegerField()
    level = models.SmallIntegerField()

    @staticmethod
    def get_player_in_match_for_hero_id(hero):
        return PlayerInMatch.objects.filter(hero=hero)

    def team(self):
        return 'Radiant' if self.player_slot <= 127 else 'Dire'

