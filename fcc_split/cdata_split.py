# this script transforms XML exports of FCC comments into directories of
# individual comments expressed as JSON including recognizing comments that are
# emails aggregated together and splitting them back apart
#
# it is specifically for the second dump of data, released on FIXME (date)

import xmltodict
from xml.parsers.expat import ExpatError
#import regex as re
import re
import json
import sys
import os
import dateutil.tz
import dateutil.parser

sys.path.append(os.getcwd())

import settings

RAW_DIR = os.path.join(settings.DATA_DIR, 'raw_xml')
JSON_DIR = os.path.join(settings.DATA_DIR, 'json', 'raw')

if not os.path.exists(JSON_DIR):
    os.mkdir(JSON_DIR)

# Lists of troublesome names

trouble_names = [
    'FCCs',
    'YouTube',
    'AdWords',
    'VoIP'
]

# Regexes

number_and_date = re.compile(
    # attempting to match what seem to be header lines, which are good
    # delimiter signals. general form seems to be (roughly):
    #
    #     [zero][digit](name)[xxxx@xxxx.xxx][date](time)
    #
    r'('
        # zero and digit
        r'(?:'
            # 0[123] not preceded by number or certain punct, and not followed
            # by certain punct. necessary for lowercase names and
            r'(?:[^0-9:=<>./\-\ ]0[123][^<>()])'
                r'|'
            # 0[123] followed by titlecase (name)
            r'(?:.0[123][A-Z][a-z])'
                r'|'
            # 0[123] followed by question marks
            r'(?:.0[123]\?\?+)'
                r'|'
            # 0[123] preceeded and followed by whitespace
            r'(?:\s0[123]\s)'
        r')'
        # name (or whatever)
        r'.{,150}?'
        # date
        r'(?:'
            # most dates look like this
            r'\d{2}/\d{2}/\d{4}'
            r'|'
            # some dates in 008 look like this
            r'\d{2}-[A-Z][a-z][a-z]-\d{2}'
        r')'
        # timestamp (not always available)
        r'(?:'
            r'\ \d{2}:\d{2}:\d{2}'
        r')*'
    r')', re.DOTALL
)

# name_and_date = re.compile(
#     # within header line,
#     r'^.*?(\d{2}/\d{2}/\d{4})')

extract_name_and_date = re.compile(
    # from a header line, extract information
    # name and email (zero or one)
    r'(?:'
        # CAPTURED: name (or whatever)
        r'(.*?)'
        # CAPTURED: email (anonymized, sometimes not there)
        r'(xxxx@xxxx.xxx)*'
    # FIXME this is hacky, covers every case except "name emailname email"
    r')??'
    # CAPTURED: date
    r'('
        # most dates look like this
        r'\d{2}/\d{2}/\d{4}'
        r'|'
        # some dates in 008 look like this
        r'\d{2}-[A-Z][a-z][a-z]-\d{2}'
    r')'
    # CAPTURED: timestamp (not always available)
    r'('
        r'\ \d{2}:\d{2}:\d{2}'
    r')*'
)

subject_line = re.compile(
        r'('
            # camel case
            r'[a-z][A-Z]'
        r')'
    r'|'
        r'('
            # number or punct followed by letter
            r'.(?![\^])[0-9.!?,)][A-Za-z]'
        r')'
    r'|'
        r'('
            # all caps mashed next to regular capitalization
            r'[A-Z][A-Z][a-z]'
        r')'
)

all_caps_subject_line = re.compile(
        # all caps sentences
            r'^'
            r'('
                    # allow A or I to start by themselves
                    r'[AI]\ '
                r'|'
                    # all others must be followed by another cap
                    r'[BCDEFGHJKLMNOPQRSTUVWXYZ]'
            r')'
            r'('
                    # continuing characters (incl spaces, non-stopping punct)
                    r'[A-Z/ \-(:;,\'"]+'
                r'|'
                    # stopping characters
                    r'[\-.!)\'"]'
            r')+'
)

# extract_heading_fields = re.compile(
#    r'[^0-9:<>./-]0[12](.*?)(\d{2}/\d{2}/\d{4})')


# Utility Fcts
def open_raw_file(file_id):
    loc = os.path.join(RAW_DIR,
                       'R-14-28-02-SOLR-Raw-{fid}.xml'.format(fid=file_id))
    return open(loc)


def write_json(out):
    outloc = os.path.join(JSON_DIR, "{msg_id}.json".format(msg_id=out['id']))
    with open(outloc, 'wb') as outf:
        json.dump(out, outf, indent=4)
    outf.close()


# Parsers, etc
def get_xml_texts(xml_file):
    try:
        doc = xmltodict.parse(xml_file.read())
        texts = [i['str'] for i in doc['doc']['arr'] if i['@name'] == 'text']
        return texts
    except ExpatError:
        from lxml import etree
        xml_file.seek(0)
        p = etree.XMLParser(huge_tree=True)
        xml = etree.parse(xml_file, p)
        xml_root = xml.getroot()
        cdata = xml_root.xpath("arr[@name='text']/str")[0]
        texts = [cdata.text, ]
        return texts



def split_first_entry(first_entry):
    split_up = re.split(extract_name_and_date, first_entry)
    first_email = split_up[-1]
    first_header = ''.join([a or '' for a in split_up[:-1]])
    return (first_header, first_email)


def chunk_text(text):
    entries = re.split(number_and_date, text)
    first_header, first_email = split_first_entry(entries[0])
    headers = [first_header, ] + entries[1::2]
    emails = [first_email, ] + entries[2::2]

    # the first character of each header goes to the end of the previous email
    for email_idx in xrange(0, len(emails)-2):
        header_idx = email_idx + 1
        emails[email_idx] = emails[email_idx] + headers[header_idx][0]
        headers[header_idx] = headers[header_idx][3:]
    return zip(headers, emails)


def parse_header(hstring):
    try:
        name, email, date, time = re.findall(extract_name_and_date, hstring)[0]
        if not time:
            time = ''

        # for records like "FCC- xxxx@xxxx.xxxFCC- xxxx@xxxx.xxx09/01/2014"
        name = name.replace('xxxx@xxxx.xxx', '')

        # for records like "Factoring AustralFactoring Austral09/02/2014"
        if not len(name) % 2:
            if name[:(len(name)/2)] == name[(len(name)/2):]:
                name = name[:(len(name)/2)]
        isodate = dateutil.parser.parse(date+' '+time).replace(
            tzinfo=dateutil.tz.tzutc()).isoformat()
        return (name.strip(), isodate)
    except ValueError as e:
        sys.stderr.write(hstring+'\n')
        sys.stderr.write(str(re.findall(extract_name_and_date, headers[0]))
                         + '\n')
        raise e


def lower_trouble(e):
    _e = e[:]
    for name in trouble_names:
        _e = _e.replace(name, name.lower())
    return _e


def lower_tweets(e):
    _e = e[:]
    return re.sub(r'(#(?:[^#\s,;]+)?)[\s,;]',
                  lambda m: m.string.replace(m.group(1), m.group(1).lower()),
                  _e)


def parse_email(email):
    # Default to no subject, msg is whole email
    subj = ''
    msg = email[:]

    # urls and newlines are good signals for a break
    dumb_split = re.split(r'(https?://|\n)', email)

    if len(dumb_split) > 1:
        maybe_subj = dumb_split[0]
        maybe_msg = ''.join(dumb_split[1:])
        # remove html entities for length measurement
        maybe_subj_len = len(re.sub(r'(&[a-z0-9#]+;)+|\s\s+', '', maybe_subj))
        if (maybe_subj_len <= 100 and (maybe_subj_len < len(maybe_msg))):
            subj = maybe_subj[:]
            msg = maybe_msg[:]

    # Try regex
    match = re.search(subject_line, lower_tweets(lower_trouble(email[:150])))
    if match:
        splitpoint = match.start() + 1
        maybe_subj = email[:splitpoint]
        maybe_msg = email[splitpoint:]
        if not (('\n' in maybe_subj) or
                (len(maybe_subj) <= 3) or
                ('http' in maybe_subj)):
            subj = maybe_subj[:]
            msg = maybe_msg[:]
    else:
        cap_match = re.search(all_caps_subject_line, email[:100])
        if cap_match and not subj:
            splitpoint = cap_match.end() - 1
            maybe_subj = email[:splitpoint]
            maybe_msg = email[splitpoint:]
            if not (('\n' in maybe_subj) or (len(maybe_subj) <= 3)):
                subj = maybe_subj[:]
                msg = maybe_msg[:]

    return (subj, msg)


if __name__ == "__main__":

    for i in sys.argv[1:]:
        headers = []
        emails = []
        msg_id = 0
        file_id = str(i).zfill(3)
        sys.stderr.write('reading {}\n'.format(file_id))
        raw_file = open_raw_file(file_id)
        for text in get_xml_texts(raw_file):
            for header, email in chunk_text(text):
                name, date = parse_header(header)
                subj, msg = parse_email(email)
                msg_id += 1
                data = {'id': '02-{fid}-{mid}'.format(
                              fid=file_id,
                              mid=str(msg_id).zfill(6)),
                        'applicant': name,
                        'text': msg,
                        'email_subject': subj,
                        'dateRcpt': date}
                write_json(data)
        sys.stderr.write('...finished {f}, wrote {m} files\n\n'.format(f=file_id,
                                                                       m=msg_id))
