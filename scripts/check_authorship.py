import os
import json
import sys

from collections import defaultdict
import re

import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import logging
logging.basicConfig(filename='log/build_es_database.log',
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


logger = logging.getLogger('debug_log')

tree_data = json.load(open(os.path.join(settings.PROJ_ROOT,'cluster_viz','tree_data','MASTER.json')))

def get_json_doc(doc_id):
    with open(os.path.join(settings.PROC_DIR,'{}.json'.format(doc_id))) as fin:
        jd = json.load(fin)
    return jd

def find_applicant_and_zip(jdoc):
    applicant = jdoc['applicant']
    if applicant:
        split_by_name = jdoc['text'].split(applicant)
        if len(split_by_name) > 1:
            address_info = split_by_name[-1]
            zips = re.findall(r'[0-9]{5}', address_info)
            if len(zips) > 0:
                return (applicant, zips[-1])
        return (applicant, None)
    else:
        return (None, None)

applicant_zipcode_counts = defaultdict(lambda: defaultdict(int))

ac_docs = ['1_1-1',
           '1_1-3',
           '2_1-0-0',
           '2_1-0-2',
           '3_1-0-3-0',
           '3_1-0-3-1',
           '4_1-0-3-2-3',
           '4_1-0-3-3-0',
           '4_1-0-3-3-1',
           '4_1-0-3-3-2',
           '4_1-0-3-3-3',
           '5_1-0-3-2-0-0',
           '5_1-0-3-2-0-1',
           '5_1-0-3-2-0-2',
           '5_1-0-3-2-1-0',
           '5_1-0-3-2-1-1',
           '5_1-0-3-2-2-1',
           '5_1-0-3-2-2-3',
           '6_1-0-3-2-1-2-0',
           '6_1-0-3-2-1-2-1',
           '6_1-0-3-2-1-2-2',
           '6_1-0-3-2-1-2-3',
           '6_1-0-3-2-1-3-1',
           '6_1-0-3-2-1-3-3',
           '7_1-0-3-2-1-3-2-0',
           '7_1-0-3-2-1-3-2-2',
           '7_1-0-3-2-1-3-2-3',
           '8_1-0-3-2-1-3-2-1-0',
           '8_1-0-3-2-1-3-2-1-1',
           '8_1-0-3-2-1-3-2-1-2']

for cluster_id in ac_docs:
    logger.info('reading docs in {}'.format(cluster_id))
    for doc_id in tree_data[cluster_id]:
        jdoc = get_json_doc(doc_id)
        applicant, zipcode = find_applicant_and_zip(jdoc)
        #print applicant, zipcode
        if applicant and zipcode:
            applicant_zipcode_counts[cluster_id][(applicant, zipcode)] += 1
