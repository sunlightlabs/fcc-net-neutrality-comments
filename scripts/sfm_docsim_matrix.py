import os
import sys
import csv
import itertools
import json

import requests
from multiprocessing import Process, Queue, JoinableQueue, cpu_count

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import settings

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('log/sfm_docsim_matrix.log')

ENDPOINT = 'http://54.87.63.230:8080/document/1/{d}/'


class Consumer(Process):
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            print '%s: %s' % (proc_name, next_task)
            status, comparisons = next_task()
            if status == 'success':
                self.task_queue.task_done()
                for comparison in comparisons:
                    self.result_queue.put(comparison)
            else:
                logger.error(comparisons)
        return


class Task(object):
    def __init__(self, doc_id):
        self.doc_id = doc_id
    def __call__(self):
        response = requests.get(ENDPOINT.format(d=self.doc_id))
        if response.status_code != 200:
            return ('error', 'bad response for doc id {d}'.format(d=self.doc_id))
        try:
            jd = response.json()
            fname = jd['title']
            char_length = jd['characters']
            associated_docs = filter(lambda x: x['docid'] > self.doc_id,
                                     jd['documents']['rows'])
            comparisons = []
            if len(associated_docs) > 0:
                for associated_doc in associated_docs:
                    associated_fname = associated_doc['title']
                    ad_chars = associated_doc['characters']
                    shared_chars = sum([f[2] for f in associated_doc['fragments']])
                    jaccard = float(shared_chars) / (float(char_length) + (float(ad_chars)))
                    comparisons.append((fname, associated_fname, jaccard))
            return ('success', comparisons)
        except Exception as e:
            return ('error', e)

    def __str__(self):
        return '%s' % (self.doc_id,)


def main():
    # Establish communication queues
    tasks = JoinableQueue()
    results = Queue()

    # Start consumers
    num_consumers = cpu_count() * 2
    print 'Creating %d consumers' % num_consumers
    consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
    for w in consumers:
        w.start()

    #num_docs = 801781
    num_docs = 100
    for i in xrange(num_docs):
        tasks.put(Task(i))

    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    # Start printing results
    with open(os.path.join(settings.PERSIST_DIR, 'doc_matrix_comparison.csv'), 'w') as fout:
        writeout = csv.writer(fout)
        while num_docs:
            if not num_docs % 1000:
                logger.info('{n} documents left'.format(n=num_docs))
            for comparison in results.get():
                writeout.writerow(comparison)
            num_docs -= 1

if __name__ == "__main__":
    multiplier = sys.argv[1]

    main()
