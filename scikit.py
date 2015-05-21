__author__ = 'Robert Waltham'
import numpy as np
import numpy.random as random
from sklearn import svm, preprocessing, neighbors
from DotaStats.models import Match, ScikitModel, Hero
import json
import time

from contextlib import contextmanager

@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))


class DotaModel():

    def __init__(self):
        pass

    @staticmethod
    def build(n_matches=2000, n_tests=200, min_duration=600):
        n_heroes = Hero.objects.all().count()
        valid_matches = []

        with timeit_context('Querying Matches'):
            matches = list(Match.objects.filter(has_been_processed=True, duration__gt=min_duration)[:n_matches].prefetch_related('playerinmatch', 'playerinmatch__hero'))
            for match in matches:
                is_valid = True
                if match.playerinmatch.all().count() != 10:
                    is_valid = False
                for playerinmatch in match.playerinmatch.all():
                    if playerinmatch.hero_id == 0 or playerinmatch.leaver_status > 0:
                        is_valid = False
                if is_valid:
                    valid_matches.append(match)

        with timeit_context('Shuffling Matches'):
            random.shuffle(valid_matches)

        training_set = valid_matches[n_tests:]
        testing_set = valid_matches[:n_tests]
        training_match_features = []
        testing_match_features = []
        training_match_win = []
        testing_match_win = []

        with timeit_context('Building Data'):
            for match in training_set:
                match_data, win = match.get_data_array(n_heroes)
                if match_data is not None:
                    training_match_features.append(match_data)
                    training_match_win.append(win)

            for match in testing_set:
                match_data, win = match.get_data_array(n_heroes)
                if match_data is not None:
                    testing_match_features.append(match_data)
                    testing_match_win.append(win)

        with timeit_context('Building Model'):
            clf = svm.SVC()
            clf.fit(training_match_features, training_match_win)

        with timeit_context('Scoring Model'):
            score = clf.score(testing_match_features, testing_match_win) * 100

        return len(valid_matches), score, training_set, testing_set


    @staticmethod
    def build_and_store(n_matches, scikit_model_id):
        matches = list(Match.objects.filter(has_been_processed=True)[:n_matches])
        model, created = ScikitModel.objects.get_or_create(id=scikit_model_id)

        clf = svm.SVC()
        match_features = []
        match_win = []

        for match in matches:
            match_data, win = match.get_data_array()
            match_features.append(match_data)
            match_win.append(win)

        clf.fit(match_features, match_win)
        model.picked_model = clf
        model.match_count = n_matches
        model.is_ready = True
        model.save()
        return model.id

    @staticmethod
    def predict(scikit_model_id, match_data):
        return ScikitModel.objects.get(id=scikit_model_id).picked_model.predict(match_data)[0]

    @staticmethod
    def build_and_test(starting_match_id, test_match_ids):
        matches = Match.objects.filter(match_id__lt=starting_match_id)
        model = ScikitModel()

        match_win = np.array([])
        match_features = np.array([])
        for match in matches:
            match_data, win = match.get_data_array()
            np.append(match_features, match_data)
            np.append(match_win, win)


        results = []
        # clf = svm.SVC()
        # match_features = []
        # match_win = []
        #
        # for match in matches:
        #     match_data, win = match.get_data_array()
        #     match_features.append(match_data)
        #     match_win.append(win)
        #
        # clf.fit(match_features, match_win)
        # model.picked_model = clf
        # model.match_count = len(matches)
        # model.is_ready = True
        # model.save()
        #
        # results = []
        # test_matches = []
        # for match_id in test_match_ids:
        #     test_matches.append(Match.objects.get(match_id=match_id))
        #
        # for match in test_matches:
        #     match_data, win = match.get_data_array()
        #     prediction = clf.predict(match_data)[0]
        #     results.append({'prediction': prediction, 'win': win, 'match_id': match.match_id})
        return results



