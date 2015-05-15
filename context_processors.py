from django.conf import settings # import the settings file


def static_settings(request):
    try:
        return {'GA_KEY': settings.GA_KEY}
    except AttributeError:
        return {}