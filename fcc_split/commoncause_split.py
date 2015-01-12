import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import json
import re


for fn in ['6018998760.json', '6018998542.json']:
    with open(os.path.join(settings.RAW_DIR, fn)) as fin:
        cc_json = json.load(fin)

    cc_list = re.split(r'\n\s\n\s\n', cc_json['text'])

    cc_list = [t for t in cc_list
               if (len(re.findall(r'(Jul|Aug|Sep)\ \d', t)) == 1
                   or
                   len(re.findall(r'Sincerely', t)) == 1)]

    cc_template = cc_json.copy()
    cc_template['text'] = ''
    base_id = cc_template.pop('id')

    for i, t in enumerate(cc_list):
        tmp = cc_template.copy()
        tmp['text'] = t
        tmp['id'] = '{b}-{n}'.format(b=base_id, n=str(i+1).zfill(4))
        filename = '{}.json'.format(tmp['id'])
        with open(os.path.join(settings.RAW_DIR, filename), 'w') as fout:
            json.dump(tmp, fout)

    sys.stderr.write('\nDone.\nRemember to delete {}.json\n'.format(base_id))
