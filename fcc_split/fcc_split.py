# this script transforms XML exports of FCC comments into directories of individual comments expressed as JSON
# including recognizing comments that are emails aggregated together and splitting them back apart

import xmltodict
import json
import sys
import os
import itertools
import re
import mailbox
import dateutil.tz
import dateutil.parser

sys.path.append(os.getcwd())

from settings import RAW_DIR

def chunkwise(t, size=2):
    it = iter(t)
    return itertools.izip(*[it]*size)

def unmangle_email(email_text, split_pattern):
    # strip out the occasional headers
    stripped = re.sub(r"\n?cimsreport_open internet [A-Z0-9a-z_-]+\.txt\[[A-Z0-9\s:/]+\]\n", "", email_text)

    # getting rid of the initial integer and dividing line
    stripped = re.split(r'^\d+\n={87}', stripped)[-1]

    # next, split into individual email messages
    split = re.split(split_pattern, stripped)
    
    messages = []
    utc = dateutil.tz.tzutc()

    # then go through them pair-wise
    for _number, message in chunkwise(itertools.islice(split, 1, None)):
        number = _number.replace(',', '')
        try:
            parsed = mailbox.Message(message.encode('utf8'))

            messages.append({
                'id': number,
                'applicant': parsed['From'].decode('utf8'),
                'email_to': parsed['To'].decode('utf8'),
                'email_subject': parsed['Subject'].decode('utf8'),
                'dateRcpt': dateutil.parser.parse(parsed['Date']).replace(tzinfo=dateutil.tz.tzutc()).isoformat(), # are they really UTC? Who knows?
                'text': parsed.get_payload().decode('utf8'),
                'preprocessed': True
            })
        except:
            messages.append({
                'id': number,
                'text': message,
                'preprocessed': True
            })

    return messages

def write_file(out):
    outf = open(os.path.join(RAW_DIR, "%s.json" % out['id']), 'w')
    outf.write(json.dumps(out, indent=4))
    outf.close()

START_PAGE_MATCH = re.compile(ur"^\d+.txt\s*", re.MULTILINE)
MID_PAGE_MATCH = re.compile(ur"\s*\d+.txt\s*Page \d+\s*", re.MULTILINE)
END_PAGE_MATCH = re.compile(ur"Page \d+\s*$", re.MULTILINE)
def strip_pagination(text):
    text = START_PAGE_MATCH.sub("", text)
    text = MID_PAGE_MATCH.sub("\n", text)
    text = END_PAGE_MATCH.sub("", text)
    return text.strip()


def handle_doc(_, doc):
    if _[-1][0] == 'doc':
        arr = {a['@name']: a for a in doc['arr']}
        print "Processing %s..." % arr['id']['long']

        out = {
            'id': arr['id']['long'],
            'applicant': arr['applicant']['str'],
            'brief': True if arr['brief']['bool'] == 'true' else False,
            'city': arr['city']['str'] if 'city' in arr else None,
            'dateRcpt': arr['dateRcpt']['date'],
            'disseminated': arr['disseminated']['date'],
            'exParte': True if arr['exParte']['bool'] == 'true' else False,
            'modified': arr['modified']['date'],
            'pages': int(arr['pages']['int']),
            'proceeding': arr['proceeding']['str'],
            'regFlexAnalysis': True if arr['regFlexAnalysis']['bool'] == 'true' else False,
            'smallBusinessImpact': True if arr['smallBusinessImpact']['bool'] == 'true' else False,
            'stateCd': arr['stateCd']['str'] if 'stateCd' in arr else None,
            'submissionType': arr['submissionType']['str'],
            'text': arr['text']['str'],
            'viewingStatus': arr['viewingStatus']['str'],
            'zip': arr['zip']['str'] if 'zip' in arr else None,
            'preprocessed': False,

            # rarer ones
            'author': arr['author']['str'] if 'author' in arr else None,
            'lawfirm': arr['lawfirm']['str'] if 'lawfirm' in arr else None,
            'fileNumber': arr['fileNumber']['str'] if 'fileNumber' in arr else None,
        }

        # really rare ones:
        for rare_type in ('reportNumber', 'daNumber', 'dateCommentPeriod', 'dateReplyComment'):
            if rare_type in arr:
                out[rare_type] = arr[rare_type]['date' if 'date' in rare_type else 'str']


        # is this a crazy emails-concatenated-together one?
        if type(out['text']) is unicode and '--------- Email' in out['text'][:1000]:
            # yes
            unmangled = unmangle_email(out['text'], "\n?--+ Email ([\d,]+) --+\n")
            for message in unmangled:
                mout = dict(out)
                mout.update(message)
                mout['id'] = '-'.join([out['id'], mout['id']])
                write_file(mout)
        elif type(out['text']) is unicode and '='*87 in out['text'][:1000]:
            # yes
            unmangled = unmangle_email(out['text'], "^={87}")
            for message in unmangled:
                mout = dict(out)
                mout.update(message)
                mout['id'] = '-'.join([out['id'], mout['id']])
                write_file(mout)
        else:
            # it's just a regular one
            if type(out['text']) is unicode and START_PAGE_MATCH.match(out['text']):
                # it needs to have pagination info stripped first, though
                out['text'] = strip_pagination(out['text'])
                out['preprocessed'] = True
            write_file(out)
    return True


if __name__ == "__main__":
    filename = sys.argv[1]
    fdir = filename.split('.')[0]
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    xmltodict.parse(open(filename), item_depth=3, item_callback=handle_doc)
