# this script transforms XML exports of FCC comments into directories of
# individual comments expressed as JSON including recognizing comments that are
# emails aggregated together and splitting them back apart
#
# it is specifically for the second dump of data, released on FIXME (date)

import xmltodict
import re
import json
import sys
import os
import dateutil.tz
import dateutil.parser

sys.path.append(os.getcwd())

import settings

RAW_DIR = os.path.join(settings.DATA_DIR, 'part_two', 'raw_xml')
JSON_DIR = os.path.join(settings.DATA_DIR, 'part_two', 'json', 'raw')

if not os.path.exists(JSON_DIR):
    os.mkdir(JSON_DIR)

# Regexes

number_and_date = re.compile(r'([^0-9:<>./-]0[12].*?\d{2}/\d{2}/\d{4})')
name_and_date = re.compile(r'^.*?(\d{2}/\d{2}/\d{4})')

extract_name_and_date = re.compile(r'(?:(.*?)(xxxx@xxxx.xxx)*)??(\d{2}/\d{2}/\d{4})')
extract_heading_fields = re.compile(r'[^0-9:<>./-]0[12](.*?)(\d{2}/\d{2}/\d{4})')


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
    doc = xmltodict.parse(xml_file.read())
    texts = [i['str'] for i in doc['doc']['arr'] if i['@name'] == 'text']
    return texts


def split_first_entry(first_entry):
    split_up = re.split(extract_name_and_date, first_entry)
    first_email = split_up[-1]
    first_header = ''.join(split_up[:-1])
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
        name, email, date = re.findall(extract_name_and_date, hstring)[0]

        # for records like "FCC- xxxx@xxxx.xxxFCC- xxxx@xxxx.xxx09/01/2014"
        name = name.replace('xxxx@xxxx.xxx', '')

        # for records like "Factoring AustralFactoring Austral09/02/2014"
        if not len(name) % 2:
            if name[:(len(name)/2)] == name[(len(name)/2):]:
                name = name[:(len(name)/2)]
        isodate = dateutil.parser.parse(date).replace(
            tzinfo=dateutil.tz.tzutc()).isoformat()
        return (name.strip(), isodate)
    except ValueError as e:
        sys.stderr.write(hstring+'\n')
        sys.stderr.write(str(re.findall(extract_name_and_date, headers[0]))
                         + '\n')
        raise e


def parse_email(email):
    m = re.search('[a-z][A-Z]', email[:100])
    if m:
        splitpoint = m.start() + 1
        subj = email[:splitpoint]
        msg = email[splitpoint:]
    else:
        if '\n' in email:
            subj = email.split('\n')[0]
            msg = '\n'.join(email.split('\n')[1:])
        else:
            subj = ''
            msg = email
    return (subj, msg)


if __name__ == "__main__":

    for i in sys.argv[1:]:
        headers = []
        emails = []
        msg_id = 0
        file_id = str(i).zfill(3)
        raw_file = open_raw_file(file_id)
        for text in get_xml_texts(raw_file):
            for header, email in chunk_text(text):
                name, date = parse_header(header)
                subj, msg = parse_email(email)
                msg_id += 1
                data = {'id': '02-{fid}-{mid}'.format(fid=file_id,
                                                      mid=str(msg_id).zfill(6)),
                        'applicant': name,
                        'text': msg,
                        'email_subject': subj,
                        'dateRcpt': date}
                write_json(data)
