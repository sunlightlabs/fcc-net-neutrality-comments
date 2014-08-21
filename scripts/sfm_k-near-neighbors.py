import csv
import sys
import itertools

from collections import defaultdict

import superfastmatch
import requests

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='log/sfm_k-near-neighbors.log', filemode='a',
                    level=logging.INFO)

logger = logging.getLogger(__file__)

sfm_url = 'http://{host}:{port}/'.format(host='0.0.0.0', port='8080')
sfm_client = superfastmatch.client.Client(url=sfm_url)

sfm_documents = superfastmatch.iterators.DocumentIterator(sfm_client, 'docid',
                                                          doctype=1,
                                                          fetch_text=True,
                                                          chunksize=100)

params = {'start': 0, 'limit': 100}
index_url = 'http://127.0.0.1:8080/index/'

similarity_matrix = defaultdict(int)

every = 1000
counter = 0

try:
    while True:
        if not counter % every:
            logger.info('{n} hashes seen, at hash {h}'.format(
                n=counter, h=params['start']))
        resp = requests.get(index_url, params=params)
        jd = resp.json()
        intersects = filter(lambda x: len(x["doctypes"][0]["docids"]) > 1,
                            jd["rows"])
        for intersect in intersects:
            shared_bytes = intersect['doctypes'][0]['bytes']
            for (a, b) in itertools.combinations(
                    intersect['doctypes'][0]['docids'], 2):
                similarity_matrix[(a, b)] += shared_bytes
        if len(jd["rows"]) < params['limit']:
            break
        else:
            next_hash = jd['rows'][-1]['hash'] + 1
            params['start'] = next_hash
        counter += 100
except Exception as e:
    raise
finally:
    with open('persistence/sfm_sim_matrix.csv', 'w') as fout:
        w = csv.writer(fout)
        w.writerows([(k[0], k[1], v) for k, v in similarity_matrix])
