import csv
import sys

import superfastmatch
from multiprocessing import Pool

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


def get_neighbors(document):
    res = sfm_client.search(document['text'])
    neighbors = [(document['title'], r['title'], r['fragment_count'], r['characters'])
                 for r in res['documents']['rows']
                 if document['docid'] < r['docid']]
    return neighbors


pool = Pool(int(sys.argv[1]))

#result = pool.imap(get_neighbors, [sfm_documents.next() for i in xrange(30)])
result = pool.imap(get_neighbors, sfm_documents)

pool.close()
pool.join()


with open('persistence/sfm_knn.csv', 'w') as fout:
    cw = csv.writer(fout)
    for neighborset in result:
        cw.writerows(neighborset)
