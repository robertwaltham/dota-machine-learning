__author__ = 'Robert Waltham'
import numpy as np
import numpy.random as random
from sklearn import svm, preprocessing, neighbors, linear_model
from DotaStats.models import Match, ScikitModel, Hero
import json
import time
import operator
from itertools import repeat, imap
from contextlib import contextmanager
from django.db.models import Q

@contextmanager
def timeit_context(name):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    print('[{}] finished in {} ms'.format(name, int(elapsed_time * 1000)))


class DotaModel():

    def __init__(self):
        pass

    @staticmethod
    def mapreduce(n_tests=1, min_duration=600):
        n_heroes = Hero.objects.all().count()
        n_matches = Match.objects.filter(has_been_processed=True,
                                            duration__gt=min_duration,
                                            valid_for_model=True).count()

        test_matches = list(Match.objects
                            .filter(has_been_processed=True,
                                                duration__gt=min_duration,
                                                valid_for_model=True)
                            .order_by('?')[:n_tests]
                            .prefetch_related('playerinmatch', 'playerinmatch__hero'))

        for match in test_matches:
            match_data, win = match.get_data_array(n_heroes)

            query = Q(has_been_processed=True) & Q(duration__gt=min_duration) & Q(valid_for_model=True)

            player_query = Q(playerinmatch__hero_id=match.playerinmatch.all()[0].hero_id)
            for player_in_match in match.playerinmatch.all()[1:]:
                player_query = player_query | Q(playerinmatch__hero_id=player_in_match.hero_id)

            training_matches = list(Match.objects
                                    .filter(query, player_query)[:5000]
                                    .prefetch_related('playerinmatch', 'playerinmatch__hero'))

            training_match_features = []
            training_match_win = []
            for training_match in training_matches:
                training_match_data, win = training_match.get_data_array(n_heroes)
                training_match_features.append(training_match_data)
                training_match_win.append(win)

            matches_by_similarity = [0 for i in repeat(None, 11)]
            wins_by_similarity = [0 for i in repeat(None, 11)]

            for i, test_match in enumerate(training_match_features):
                score = int(sum(imap(operator.mul, match_data, test_match)))
                matches_by_similarity[score] += 1
                if training_match_win[i]:
                    wins_by_similarity[score] += 1

            print matches_by_similarity
            print wins_by_similarity
            # print map(lambda x: str(100 * float(x) / n_matches) + '%', matches_by_similarity)
            print list(imap(lambda x, y: str(100 * float(x) / float(y)) + '%' if y > 0 else '0%', wins_by_similarity, matches_by_similarity))


    @staticmethod
    def build(n_matches=2000, n_tests=200, min_duration=600, algorithm='SVC'):
        n_heroes = Hero.objects.all().count()
        valid_matches = []
        radiant_win = 0
        dire_win = 0

        with timeit_context('Querying Matches'):
            matches = list(Match.objects.filter(has_been_processed=True,
                                                duration__gt=min_duration,
                                                valid_for_model=True).order_by('?')[:n_matches]
                           .prefetch_related('playerinmatch', 'playerinmatch__hero'))
            for match in matches:
                is_valid = True
                if match.playerinmatch.all().count() != 10:
                    is_valid = False
                for playerinmatch in match.playerinmatch.all():
                    if playerinmatch.hero_id == 0 or playerinmatch.leaver_status > 0:
                        is_valid = False
                if is_valid:
                    valid_matches.append(match)
                    if match.radiant_win:
                        radiant_win += 1
                    else:
                        dire_win += 1

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

        with timeit_context('Building Model ' + algorithm):
            clf = None
            if algorithm == 'SVC':
                clf = svm.SVC()
            if algorithm == 'SGD':
                clf = linear_model.SGDClassifier()
            clf.fit(training_match_features, training_match_win)

        with timeit_context('Scoring Model'):
            score = clf.score(testing_match_features, testing_match_win) * 100

        return len(valid_matches), score,\
            (float(radiant_win) / float(len(valid_matches))) * 100


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



