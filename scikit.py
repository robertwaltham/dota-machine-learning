__author__ = 'Robert Waltham'
import numpy as np
from sklearn import svm, preprocessing
from DotaStats.models import Match, ScikitModel
import json


class DotaModel():

    def __init__(self):
        pass

    @staticmethod
    def build():
        n_tests = 100
        matches = Match.objects.filter(has_been_processed=True)
        clf = svm.SVC()
        match_features = []
        match_win = []

        for match in matches[n_tests:]:
            match_data, win = match.get_data_array()
            match_features.append(match_data)
            match_win.append(win)

        clf.fit(match_features, match_win)

        results = []
        count = 0
        for match in matches[:n_tests]:
            match_data, win = match.get_data_array()
            predict = clf.predict(match_data)[0]
            results.append({'id': match.match_id, 'win': win, 'predict': predict})
            if win == predict:
                count += 1
        return results, (float(count) / float(n_tests)) * 100

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

        clf = svm.SVC()
        match_features = []
        match_win = []

        for match in matches:
            match_data, win = match.get_data_array()
            match_features.append(match_data)
            match_win.append(win)

        clf.fit(match_features, match_win)
        model.picked_model = clf
        model.match_count = len(matches)
        model.is_ready = True
        model.save()

        results = []
        test_matches = []
        for match_id in test_match_ids:
            test_matches.append(Match.objects.get(match_id=match_id))

        for match in test_matches:
            match_data, win = match.get_data_array()
            prediction = clf.predict(match_data)[0]
            results.append({'prediction': prediction, 'win': win, 'match_id': match.match_id})
        return results



