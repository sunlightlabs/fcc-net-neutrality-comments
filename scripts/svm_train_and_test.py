import sys
import os
import csv
import json
import time

import numpy as np
import pandas as pd

from libshorttext.converter import Text2svmConverter, FeatureGenerator, TextPreprocessor, convert_text
from libshorttext.classifier import TextModel, train_converted_text, predict_text

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import settings as ls

project_name = 'fcc-experts'
BASE_DIR = ls.SVM_DIR

DATA_DIR = os.path.join(BASE_DIR, 'data')
CLEAN_DIR = os.path.join(DATA_DIR, 'clean')
TRAIN_DIR = os.path.join(DATA_DIR, 'labeled', 'train')
TEST_DIR = os.path.join(DATA_DIR, 'labeled', 'test')
CONVERTER_DIR = os.path.join(BASE_DIR, 'converters')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
RESULT_DIR = os.path.join(BASE_DIR, 'results')
OPTIONS_DIR = os.path.join(BASE_DIR, 'options')

train_csv = os.path.join(CLEAN_DIR, project_name + '_train.csv')
test_csv = os.path.join(CLEAN_DIR, project_name + '_test.csv')

train_svm = os.path.join(TRAIN_DIR, project_name + '_train.svm')
test_svm = os.path.join(TEST_DIR, project_name + '_test.svm')

options_json = os.path.join(OPTIONS_DIR, project_name + '_options.json')
        
converter_path = os.path.join(CONVERTER_DIR, project_name + '.converter')

model_path = os.path.join(MODEL_DIR, project_name+'.model')

result_path = os.path.join(RESULT_DIR, project_name+'.result')

def make_dirs(dirlist):
    for d in dirlist:
        if not os.path.exists(d):
            os.makedirs(d)

def make_options():
    options = {}

    # STEMMING: 1 to use porter, 0 for no stemming, or give your 
    #           own stemmer that maps from a list of tokens to a 
    #           list of stemmed tokens
    options['stemming'] = ls.svm_options.get('stemming', 1)

    # STOPWORDS: 1 to use default stops, 0 for no stops, or give
    #            a list of stopwords to be used
    options['stopword'] = ls.svm_options.get('stopword', 1)

    # NGRAM: 1 to use bigram, 0 to use unigram
    options['ngram'] = ls.svm_options.get('ngram', 1)

    json.dump(options, open(options_json, 'w'), indent=2)
    return options

sys.stderr.write('making dirs\n')
make_dirs([DATA_DIR, CLEAN_DIR, TRAIN_DIR, TEST_DIR, MODEL_DIR, RESULT_DIR, 
            OPTIONS_DIR, CONVERTER_DIR])

sys.stderr.write('making options\n')
options = make_options()

if not os.path.exists(converter_path):
    sys.stderr.write('no converter. making one\n')
    start_time = time.time()
    # Make text processor
    tp_option_str = "-stopword {stopword} -stemming {stemming}".format(**options)
    text_processor = TextPreprocessor(option=tp_option_str)

    # Make feature generator
    fg_option_str = "-feature {ngram}".format(**options)
    feature_generator = FeatureGenerator(option=fg_option_str)

    # Make converter
    text_converter = Text2svmConverter()
    text_converter.feat_gen = feature_generator
    text_converter.text_prep = text_processor

    # Convert Text
    convert_text(train_csv, text_converter, train_svm)
    sys.stderr.write('...converter making took {} seconds\n'.format(time.time() - start_time))

    # Save Converter
    text_converter.save(converter_path)
    sys.stderr.write('...converter saved to {}\n'.format(converter_path))
else:
    sys.stderr.write('found saved converter at {}\n'.format(converter_path))
    text_converter = Text2svmConverter()
    text_converter.load(converter_path)

if not os.path.exists(model_path):
    sys.stderr.write('no model. training one\n')
    start_time = time.time()
    text_model = train_converted_text(train_svm, text_converter)
    sys.stderr.write('...training took {} seconds\n'.format(time.time() - start_time))
    text_model.save(model_path)
    sys.stderr.write('...model saved to {}\n'.format(model_path))
else:
    sys.stderr.write('found saved model at {}\n'.format(model_path))
    text_model = TextModel(model_path)

sys.stderr.write('testing... \n'.format(converter_path))

prediction_result = predict_text(test_csv, text_model)
prediction_result.save(result_path, analyzable=True)

sys.stderr.write('prediction accuracy was {}\n'.format(
                  prediction_result.get_accuracy()))
sys.stderr.write('prediction results analyzable in {}\n'.format(result_path))
