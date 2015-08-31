from django.contrib.auth.models import User, Group
from rest_framework import serializers

from models import Hero, Match, PlayerInMatch, Item


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, item):
        return item.get_image()

    class Meta:
        model = Item
        fields = ('item_id', 'image', 'name', 'localized_name', 'url')


class HeroSerializer(serializers.ModelSerializer):
    hero_image = serializers.SerializerMethodField()
    small_hero_image = serializers.SerializerMethodField()

    def get_hero_image(self, hero):
        return hero.get_image()

    def get_small_hero_image(self, hero):
        return hero.get_small_image()

    class Meta:
        model = Hero
        fields = ('name', 'localized_name', 'hero_id', 'url', 'primary_attribute', 'hero_image', 'small_hero_image')


class PlayerInMatchSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(many=False, read_only=True)
    item_0 = ItemSerializer(read_only=True)
    item_1 = ItemSerializer(read_only=True)
    item_2 = ItemSerializer(read_only=True)
    item_3 = ItemSerializer(read_only=True)
    item_4 = ItemSerializer(read_only=True)
    item_5 = ItemSerializer(read_only=True)

    class Meta:
        model = PlayerInMatch

        fields = ('player_slot', 'hero', 'item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5',)


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    playerinmatch = PlayerInMatchSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = ('match_id', 'url', 'radiant_win', 'playerinmatch')

