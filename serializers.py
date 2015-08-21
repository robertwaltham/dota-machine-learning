from django.contrib.auth.models import User, Group
from rest_framework import serializers

from models import Hero


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


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