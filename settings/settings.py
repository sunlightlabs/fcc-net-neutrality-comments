import os

PROJ_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         os.path.pardir)

DATA_DIR = os.path.join(PROJ_ROOT, 'data')
JSON_DIR = os.path.join(DATA_DIR, 'json')
XML_DIR = os.path.join(DATA_DIR, 'json')
STATS_DIR = os.path.join(PROJ_ROOT, 'stats')
PROC_DIR = os.path.join(JSON_DIR, 'processed')
PERSIST_DIR = os.path.join(PROJ_ROOT, 'persistence')
