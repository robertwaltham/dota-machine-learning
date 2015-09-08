import json
import urllib2
import datetime
import pytz
import numpy

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from models import Hero, Item

API_BASE = 'https://api.steampowered.com'
API_MATCH_HISTORY = '/IDOTA2Match_570/GetMatchHistory/V001/'
API_MATCH_HISTORY_SEQUENCE = '/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?key={0}&start_at_match_seq_num={1}'
API_DETAILS = '/IDOTA2Match_570/GetMatchDetails/V001/?match_id={0}&key={1}'
API_HERO_STATS_URL = 'http://herostats.io:322/heroes/all'
API_ITEMS_URL = 'https://api.steampowered.com/IEconDOTA2_570/GetGameItems/v0001/?key={0}&language={1}'
API_HEROES_URL = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v001/?key={0}&language={1}'

API_LANGUAGE = 'en_us'


class DotaApi:
    @staticmethod
    def load_heroes_from_api():
        url = API_HEROES_URL.format(settings.DOTA_API_KEY, API_LANGUAGE)
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
            for key, hero_data in json.load(urllib2.urlopen(API_HERO_STATS_URL)).iteritems():
                try:
                    hero = Hero.objects.get(localized_name=hero_data['Name'])
                    hero.primary_attribute = hero_data['PrimaryStat']
                    hero.save()
                except ObjectDoesNotExist as e:
                    print "ObjectDoesNotExist " + hero_data['Name']
            return result
        except urllib2.HTTPError as e:
            return "HTTP error({0}): {1}".format(e.errno, e.strerror)

    @staticmethod
    def load_items_from_api():
        url = API_ITEMS_URL.format(settings.DOTA_API_KEY, API_LANGUAGE)
        try:
            data = json.load(urllib2.urlopen(url))
            result = 0
            if data['result']['status'] == 200:
                # Make sure an empty item exists
                item, created = Item.objects.get_or_create(item_id=0)

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

    @staticmethod
    def get_match_api_url(game_mode=0, skill=0, date_min=0, date_max=0, min_players=10,
                          start_at_match_id=0, matches_requested=100):

        url = API_BASE + API_MATCH_HISTORY + '?key=' + settings.DOTA_API_KEY
        # api is bugged and doesn't honor game mode flag
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
    def get_new_matches_by_sequence_from_api(match_seq_num=None):
        from DotaStats.tasks import process_match

        # get sequence number of latest match
        if not match_seq_num:
            latest_match_url = DotaApi.get_match_api_url(matches_requested=1)
            try:
                latest_match_data = json.load(urllib2.urlopen(latest_match_url))
                if latest_match_data['result']['status'] == 1:
                    match_seq_num = latest_match_data['result']['matches'][0]['match_seq_num']
                else:
                    return "API Error {0}".format(latest_match_data['result']['status'])

            except urllib2.HTTPError as e:
                return "HTTP error({0}): {1}".format(e.errno, e.strerror)

        api_has_more_matches = True
        n_matches_created = 0
        requests = 0

        # get matches until there are no new matches
        while api_has_more_matches:
            match_seq_url = API_BASE + API_MATCH_HISTORY_SEQUENCE.format(settings.DOTA_API_KEY, match_seq_num)
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

            # sanity
            requests += 1
            if requests >= 5:
                break

        return "Created: {0} Requests: {1}".format(n_matches_created, requests)
