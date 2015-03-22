from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Player(models.Model):
    name = models.CharField(max_length=255)


class Hero(models.Model):
    name = models.CharField(max_length=255)


class Item(models.Model):
    name = models.CharField(max_length=255)

# CREATE TABLE MATCH (
# match_id int unsigned PRIMARY KEY,
# start_time datetime NOT NULL,
# match_seq_num int unsigned NOT NULL,
# has_been_processed bool NOT NULL DEFAULT FALSE,
# radiant_win bool,
# duration int unsigned,
# tower_status_radiant smallint unsigned,
# tower_status_dire smallint unsigned,
# barracks_status_radiant smallint unsigned,
# barracks_status_dire smallint unsigned,
# cluster int unsigned,
# first_blood_time smallint unsigned,
# lobby_type tinyint unsigned,
# human_players tinyint unsigned,
# leagueid tinyint unsigned,
# game_mode tinyint unsigned
# ) ENGINE = MyISAM


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

    @staticmethod
    def get_all():
        return Match.objects.all()

# "match_id": int unsigned,
# "account_id": int unsigned,
# "player_slot": tinyint unsigned,
# "hero_id": smallint unsigned,
# "item_0": smallint unsigned,
# "item_1": smallint unsigned,
# "item_2": smallint unsigned,
# "item_3": smallint unsigned,
# "item_4": smallint unsigned,
# "item_5": smallint unsigned,
# "kills": smallint unsigned,
# "deaths": smallint unsigned,
# "assists": smallint unsigned,
# "leaver_status": tinyint unsigned,
# "gold": smallint unsigned,
# "last_hits": smallint unsigned,
# "denies": smallint unsigned,
# "gold_per_min": smallint unsigned,
# "xp_per_min": smallint unsigned,
# "gold_spent": smallint unsigned,
# "hero_damage": smallint unsigned,
# "tower_damage": smallint unsigned,
# "hero_healing": smallint unsigned,
# "level": tinyint unsigned,


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

