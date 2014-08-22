
# coding: utf-8

## Imports

# In[28]:

import os
import sys
import json
from random import sample
from glob import iglob


# In[2]:


sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import settings


# In[23]:

from models.util import clean_text
from nltk.tokenize import sent_tokenize

def get_json(filename):
    return json.load(open(os.path.join(settings.RAW_DIR, filename)))

def get_text(jd):
    return jd['text']

def get_sentences(filename):
    return get_text(get_json(filename))

law_firm_docs = [line.strip() for line in open(os.path.join(settings.STATS_DIR,
                                                            'lawfirm_docs.txt'))]


fnames = [os.path.basename(d) for d in iglob(os.path.join(settings.RAW_DIR, '*.json'))]


lfdoc_ix = [fnames.index(law_firm_doc) for law_firm_doc in law_firm_docs]

with open(os.path.join(settings.SVM_DIR, 'expert_sentences.csv'), 'w') as fout:
    seen = []
    for d in law_firm_docs:
        seen.append(d)
        sentences = sent_tokenize(get_text(get_json(fnames[lfdoc_ix[0]])))
        for sentence in sentences:
            fout.write('\t'.join(['EXPERT',
                                  clean_text(sentence).replace('\n',' ').replace('\t',' ')]))
            fout.write('\n')
    count = 1000
    while count:
        d = sample(fnames, 1)
        if d in seen:
            continue
        else:
            sentences = sent_tokenize(get_text(get_json(fnames[lfdoc_ix[0]])))
            for sentence in sentences:
                fout.write('\t'.join(['JOE',
                                      clean_text(sentence).replace('\n',' ').replace('\t',' ')]))
                fout.write('\n')
            count -= 1
