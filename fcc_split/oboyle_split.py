import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import json
import re


for fn in ['6018996416.json', '6018997289.json']:
    with open(os.path.join(settings.RAW_DIR, fn)) as fin:
        ob_json = json.load(fin)

    ob_list = re.split(r'\n\s?\n\n', ob_json['text'])

    ob_list = [t for t in ob_list
               if len(re.findall(r'(Jul|Aug|Sep)\ \d', t)) == 1]

    ob_template = ob_json.copy()
    ob_template['text'] = ''
    base_id = ob_template.pop('id')

    for i, t in enumerate(ob_list):
        tmp = ob_template.copy()
        tmp['text'] = t
        tmp['id'] = '{b}-{n}'.format(b=base_id, n=str(i+1).zfill(4))
        filename = '{}.json'.format(tmp['id'])
        with open(os.path.join(settings.RAW_DIR, filename), 'w') as fout:
            json.dump(tmp, fout)

    sys.stderr.write('\nDone.\nRemember to delete {}.json\n'.format(base_id))
