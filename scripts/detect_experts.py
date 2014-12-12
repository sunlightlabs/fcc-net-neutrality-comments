import os
import sys
import csv
import json

# import requests
# from multiprocessing import Process, Queue, JoinableQueue, cpu_count

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import settings

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('log/detect_experts.log')

from libshorttext import classifier
from AsciiDammit import asciiDammit

logger.info('initiating textmodel')
svm_model = classifier.TextModel('svm_experts/models/fcc-experts.model')

logger.info('listing documents')
doc_ids = [line.strip() for line in open(os.path.join(settings.PERSIST_DIR,
                                                    'document_index_part_two'), 'r')]
logger.info('... found {} documents'.format(len(doc_ids)))


def get_json(filename):
    return json.load(open(os.path.join(settings.PROC_DIR, filename)))


def get_text(jd):
    txt = jd.get('text', "")
    if txt:
        return asciiDammit(txt)
    else:
        return ""


with open(os.path.join(settings.PERSIST_DIR, 'expert_predictions_part_two.csv'), 'w') as fout:
    writer = csv.writer(fout)
    for i, doc_id in enumerate(doc_ids):
        fname = '{}.json'.format(doc_id)
        if not i % 1000:
            logger.info('predicted {} documents'.format(i))
        result = classifier.predict_single_text(get_text(get_json(fname)),
                                                svm_model)
        writer.writerow((fname, result.predicted_y, result.decvals[0], result.decvals[1]))
