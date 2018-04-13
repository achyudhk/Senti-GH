from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.utils import resample
from nltk.classify import NaiveBayesClassifier
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
import pandas as pd
import numpy as np


def train(train_x, train_y):
    train_x = list(zip(train_x, train_y))
    sentim_analyzer = SentimentAnalyzer()
    all_words_neg = sentim_analyzer.all_words([mark_negation(doc) for doc in train_x])
    unigram_feats = sentim_analyzer.unigram_word_feats(all_words_neg, min_freq=5)
    sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)
    training_set = sentim_analyzer.apply_features(train_x)
    trainer = NaiveBayesClassifier.train
    classifier = sentim_analyzer.train(trainer, training_set)
    return sentim_analyzer, classifier


def predict(sentim_analyzer, classifier, predict_x):
    test_set = sentim_analyzer.apply_features(predict_x, labeled=False)
    predict_y = classifier.classify_many(test_set)
    return predict_y


def evaluate(sentim_analyzer, classifier, evaluate_x, evaluate_y):
    predict_y = predict(sentim_analyzer, classifier, evaluate_x)
    return {"individual": precision_recall_fscore_support(evaluate_y, predict_y),
            "micro-average": precision_recall_fscore_support(evaluate_y, predict_y, average="micro")}


def cross_val(data_x, data_y, num_classes, n_splits=5):
    skf = StratifiedKFold(n_splits, random_state=157)
    print("Performing cross validation (%d-fold)..." % n_splits)
    precision_list = [0 for i in range(num_classes)]
    recall_list = [0 for i in range(num_classes)]
    mean_accuracy = 0
    for train_index, test_index in skf.split(data_x, data_y):
        sentim_analyzer, classifier = train(data_x[train_index], data_y[train_index])
        metrics = evaluate(sentim_analyzer, classifier, data_x[test_index], data_y[test_index])
        precision_list = [x + y for x, y in zip(metrics['individual'][0], precision_list)]
        recall_list = [x + y for x, y in zip(metrics['individual'][1], recall_list)]
        mean_accuracy += metrics['micro-average'][0]
        print("Precision, Recall, F_Score, Support")
        print(metrics)
    print("Mean accuracy: %s Mean precision: %s, Mean recall: %s" % (mean_accuracy/n_splits, [precision/n_splits for precision in precision_list], [recall/n_splits for recall in recall_list]))


def bootstrap_trend(data_x, data_y):
    train_x, test_x, train_y, test_y = train_test_split(data_x, data_y, test_size=0.2, random_state=157)
    print("Metrics: Precision, Recall, F_Score, Support")
    precision_list = list()
    recall_list = list()
    accuracy_list = list()
    for sample_rate in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        n_samples = int(sample_rate * len(train_y) + 1)
        train_xr, train_yr = resample(train_x, train_y, n_samples=n_samples, random_state=157)
        print("Training with %d samples", len(train_yr))
        sentim_analyzer, classifier = train(train_xr, train_yr)
        metrics = evaluate(sentim_analyzer, classifier, test_x, test_y)
        accuracy_list.append(metrics['micro-average'][0])
        print(metrics)
    print(accuracy_list)

if __name__ == '__main__':
    num_classes = 2
    # data = pd.read_csv("data/labelled/JIRA.csv").as_matrix()
    # data = pd.read_csv("data/labelled/StackOverflow.csv", encoding='latin1').as_matrix()
    data_1 = pd.read_csv("data/labelled/Gerrit.csv")
    data_2 = pd.read_csv("data/labelled/JIRA.csv")
    data_3 = pd.read_csv("data/labelled/StackOverflow2.csv", encoding='latin1')
    data = pd.concat([data_1, data_2, data_3]).as_matrix()
    data_x = np.array([x.lower().split() for x in data[:,0]])
    data_y = np.array([int(x) for x in data[:,1]])
    print("Dataset loaded to memory. Size:", len(data_y))
    # cross_val(data_x, data_y, num_classes, n_splits=10)
    bootstrap_trend(data_x, data_y)