# this script transforms XML exports of FCC comments into directories of individual comments expressed as JSON
# including recognizing comments that are emails aggregated together and splitting them back apart

import xmltodict, json, sys, os, itertools, re
import mailbox
import dateutil.tz, dateutil.parser

def chunkwise(t, size=2):
    it = iter(t)
    return itertools.izip(*[it]*size)

def unmangle_email(email_text):
    # strip out the occasional headers
    stripped = re.sub(r"\n?cimsreport_open internet [A-Z0-9a-z_-]+\.txt\[[A-Z0-9\s:/]+\]\n", "", email_text)

    # next, split into individual email messages
    split = re.split("\n?--+ Email ([\d,]+) --+\n", stripped)

    
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
    outf = open(os.path.join(fdir, "%s.json" % out['id']), 'w')
    outf.write(json.dumps(out, indent=4))
    outf.close()

def handle_doc(_, doc):
    if _[-1][0] == 'doc':
        arr = {a['@name']: a for a in doc['arr']}
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
            'preprocessed': False
        }

        # is this a crazy emails-concatenated-together one?
        if type(out['text']) is unicode and '--------- Email' in out['text'][:1000]:
            # yes
            unmangled = unmangle_email(out['text'])
            for message in unmangled:
                mout = dict(out)
                mout.update(message)
                mout['id'] = '-'.join([out['id'], mout['id']])
                write_file(mout)
        else:
            # it's just a regular one
            write_file(out)
    return True


if __name__ == "__main__":
    filename = sys.argv[1]
    fdir = filename.split('.')[0]
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    xmltodict.parse(open(filename), item_depth=3, item_callback=handle_doc)