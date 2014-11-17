import os

PROJ_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         os.path.pardir)

DATA_DIR = os.path.join(PROJ_ROOT, 'data')
JSON_DIR = os.path.join(DATA_DIR, 'json')
XML_DIR = os.path.join(DATA_DIR, 'raw_xml')
STATS_DIR = os.path.join(PROJ_ROOT, 'stats')
RAW_DIR = os.path.join(JSON_DIR, 'raw')
PROC_DIR = os.path.join(JSON_DIR, 'processed')
PERSIST_DIR = os.path.join(PROJ_ROOT, 'persistence')
SVM_DIR = os.path.join(PROJ_ROOT, 'svm_experts')
CLUSTER_DIR = os.path.join(PERSIST_DIR, 'clusters')

svm_options = {
    'stemming': 1,
    'stopword': 0,
    'ngram': 1,
    
}
