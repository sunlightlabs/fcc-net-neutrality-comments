
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
    text = jd['text']
    return text or ""

def get_sentences(filename):
    return get_text(get_json(filename))

law_firm_docs = [line.strip() for line in open(os.path.join(settings.STATS_DIR,
                                                            'lawfirm_docs.txt'))]


fnames = [os.path.basename(d) for d in iglob(os.path.join(settings.RAW_DIR, '*.json'))]


lfdoc_ix = [fnames.index(law_firm_doc) for law_firm_doc in law_firm_docs]

def write_sentence(sentence, tag, outfile):
    outfile.write('\t'.join([tag,
                          clean_text(sentence).replace('\n',' ').replace('\t',' ')]))
    outfile.write('\n')

CLEAN_DIR = os.path.join(settings.SVM_DIR, 'data', 'clean')

trainfile = open(os.path.join(CLEAN_DIR, 'fcc-experts_train.csv'),'w')
testfile = open(os.path.join(CLEAN_DIR, 'fcc-experts_test.csv'),'w')

seen = set([])
count = 0
for i, d in enumerate(law_firm_docs):
    #if d == '6017986294.json':
    #    continue
    seen.add(d)
    sentences = sent_tokenize(get_text(get_json(d)))
    try:
        for sentence in sentences:
            if not count % 10:
                # send ~every tenth sentence to test
                write_sentence(sentence, 'EXPERT', testfile)
            else:
                write_sentence(sentence, 'EXPERT', trainfile)
            count += 1
    except:
        print d
        raise

while count:
    d = sample(fnames, 1)[0]
    if d in seen:
        continue
    else:
        seen.add(d)
        sentences = sent_tokenize(get_text(get_json(d)))
        for sentence in sentences:
            if not count % 10:
                # send ~every tenth sentence to test
                write_sentence(sentence, 'JOE', testfile)
            else:
                write_sentence(sentence, 'JOE', trainfile)
                sentences = sent_tokenize(get_text(get_json(fnames[lfdoc_ix[0]])))
            count -= 1
