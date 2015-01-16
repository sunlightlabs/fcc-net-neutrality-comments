import sys
import os
import logging
from glob import iglob

logging.basicConfig(filename='build_corpus_and_dictionary.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir))

from gensim.corpora import dictionary

import settings
from models import tokenizer
from models import corpus


punct_tags = list(',.:)"') + ['CD', 'IN']

pt_tokenizer = tokenizer.PretaggedTokenizer(stopword_list=None, filter_tags=punct_tags)
lj_corpus = corpus.LazyJSONCorpus(tokenizer=pt_tokenizer, dictionary=None, path_to_text="tagged")

glob_pattern = os.path.join(settings.PROC_DIR, '*.json')
#glob_pattern = os.path.join(settings.PROC_DIR, '60182*.json')
lj_corpus.glob_documents(glob_pattern)
with open(os.path.join(settings.PERSIST_DIR, 'document_index'), 'w') as fout:
    for floc in iglob(glob_pattern):
        doc_id = os.path.basename(floc).split('.')[0]
        fout.write(doc_id+'\n')

my_dict = dictionary.Dictionary(lj_corpus)


lj_corpus.dictionary = my_dict

my_dict.save(os.path.join(settings.PERSIST_DIR, 'my_dict'))
