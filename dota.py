import requests

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
    # load data from Dota 2 API
    def load_heroes_from_api():
        url = API_HEROES_URL.format(settings.DOTA_API_KEY, API_LANGUAGE)
        r = requests.get(url)
        r.raise_for_status()
        hero_count = 0
        if r.status_code == requests.codes.ok:
            data = r.json()
            hero_count = len(data['result']['heroes'])
            for new_hero in data['result']['heroes']:
                hero, created = Hero.objects.get_or_create(hero_id=new_hero['id'])
                hero.name = new_hero['name']
                hero.localized_name = new_hero['localized_name']
                hero.save()
        return hero_count

    # load data from secondary API
    @staticmethod
    def load_hero_attribute_from_api():
        r = requests.get(API_HERO_STATS_URL)
        r.raise_for_status()
        hero_count = 0
        data = r.json()
        for key, hero_data in data.iteritems():
            try:
                hero = Hero.objects.get(localized_name=hero_data['Name'])
                hero.primary_attribute = hero_data['PrimaryStat']
                hero.save()
                hero_count += 1
            except ObjectDoesNotExist as e:
                print "ObjectDoesNotExist " + hero_data['Name']
        return hero_count

    # load item data from Dota 2 API
    @staticmethod
    def load_items_from_api():
        url = API_ITEMS_URL.format(settings.DOTA_API_KEY, API_LANGUAGE)
        r = requests.get(url)
        r.raise_for_status()
        item_count = 0
        if r.status_code == requests.codes.ok:
            data = r.json()
            # Make sure an empty item exists
            item, created = Item.objects.get_or_create(item_id=0)
            item_count = len(data['result']['items'])
            for new_item in data['result']['items']:
                item, created = Item.objects.get_or_create(item_id=new_item['id'])
                item.name = new_item['name']
                item.recipe = bool(new_item['recipe'])
                item.secret_shop = bool(new_item['secret_shop'])
                item.side_shop = bool(new_item['side_shop'])
                item.localized_name = new_item['localized_name']
                item.cost = int(new_item['cost'])
                item.save()
        return item_count

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
    def load_matches_from_api_by_sequence_number(match_sequence_number=None):
        from DotaStats.tasks import process_match

        match_seq_url = API_BASE + API_MATCH_HISTORY_SEQUENCE.format(settings.DOTA_API_KEY, match_sequence_number)
        r = requests.get(match_seq_url)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            match_data = r.json()
            if match_data['result']['status'] == 1:
                if len(match_data['result']['matches']) == 0:
                    return False

                for match in match_data['result']['matches']:
                    process_match.apply_async((match,))
                    if int(match['match_seq_num']) > match_sequence_number:
                        match_sequence_number = int(match['match_seq_num'])
                return match_sequence_number
            else:
                return False

    @staticmethod
    def load_matches_from_api():
        latest_match_url = DotaApi.get_match_api_url(matches_requested=1)
        r = requests.get(latest_match_url)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            latest_match_data = r.json()
            if latest_match_data['result']['status'] == 1:
                match_seq_num = latest_match_data['result']['matches'][0]['match_seq_num']

                # get matches until there are no new matches, max 10 requests
                for i in range(0, 10):
                    if match_seq_num is not False:
                        match_seq_num = DotaApi.load_matches_from_api_by_sequence_number(match_sequence_number=match_seq_num)
                    else:
                        break
