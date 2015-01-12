import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import json
import re


with open(os.path.join(settings.RAW_DIR, '6018233706.json')) as fin:
    hp_json = json.load(fin)


hp_list = re.split(r'(?![.])\n\n', hp_json['text'])

hangovers = [hp_list.index(t) for t in hp_list
             if len(re.findall(r'^Chairman', t)) != 1]

for hangover in hangovers:
    hp_list[hangover-1] + hp_list[hangover]

new_hp_list = [t for i, t in enumerate(hp_list) if i not in hangovers]

hp_template = hp_json.copy()
hp_template['text'] = ''
base_id = hp_template.pop('id')

for i, t in enumerate(new_hp_list):
    tmp = hp_template.copy()
    tmp['text'] = t
    tmp['id'] = '{b}-{n}'.format(b=base_id, n=str(i+1).zfill(4))
    filename = '{}.json'.format(tmp['id'])
    with open(os.path.join(settings.RAW_DIR, filename), 'w') as fout:
        json.dump(tmp, fout)

sys.stderr.write('\nDone.\nRemember to delete {}.json\n'.format(base_id))
