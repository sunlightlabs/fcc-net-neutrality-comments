import subprocess
import json
import sys
import os

from util import clean_text


def gposttl(utterance, identifier="no_id"):
    utterance = clean_text(utterance)
    p = subprocess.Popen(['gposttl', '--silent'], stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    (out, error) = p.communicate(utterance.encode('utf8'))
    if p.returncode != '0':
        if len(out) > 1:
            out = out.decode('utf8')
            tokens = [a.replace(u'\t', u'|')
                      for a in out.split(u'\n')
                      if len(a) > 0]
            return tokens
        else:
            raise Exception('Error: no text to parse')
    else:
        msg = str(error)
        code = str(p.returncode)
        raise Exception(': '.join([identifier, code, msg]))


def tag_content(s):
    tagged_content = ' '.join(gposttl(s))
    return tagged_content


def process_file(file_loc):
    jdict = json.load(open(file_loc, 'r'))
    jdict['tagged'] = tag_content(jdict['text'])
    return jdict

if __name__ == "__main__":
    try:
        output_dir = sys.argv[1]
        processed = process_file(sys.argv[2])
        output_loc = os.path.join(output_dir, processed['id'] + '.json')
        with open(output_loc, 'w') as output_file:
            json.dump(processed, output_file)
    except Exception as e:
        sys.stderr.write('something went wrong with pos_tagger\n')
        sys.stderr.write('output_dir: {d}\n'.format(d=sys.argv[1]))
        sys.stderr.write('file: {d}\n\n'.format(d=sys.argv[2]))
        raise e
