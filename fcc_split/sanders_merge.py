import re, json, sys, os

print "Building ligature correction regex...",
_ligatures_dict = dict(json.load(open("sanders_ligatures.json")))
_ligatures_re = re.compile("(%s)" % "|".join(map(re.escape, _ligatures_dict.keys())), flags=re.I)
def fix_ligatures(text):
    return _ligatures_re.sub(lambda mo: _ligatures_dict[mo.string[mo.start():mo.end()].lower()], text)
print "done."

# built up a dictionary of common words
print "Building dictionary...",
import nltk, nltk.corpus
letters = re.compile(r"[a-z]")
all_words = [w.lower() for w in nltk.corpus.brown.words() if letters.search(w)]
freqs = nltk.FreqDist(all_words)
most_common = set(
    sorted(set(all_words), key=lambda x: freqs[x], reverse=True)[:100000]
)
most_common.update(['internet', 'fcc', 'infiltrate'])
print "done."

# prep some date stuff
import dateutil.parser, dateutil.tz
utc = dateutil.tz.tzutc()

# original metadata
orig_meta = {
    "city": "Washington",
    "zip": "20510",
    "proceeding": "14-28",
    "regFlexAnalysis": False,
    "exParte": False,
    "stateCd": "DC",
    "submissionType": "COMMENT",
    "disseminated": "2014-07-17T16:19:19.233Z",
    "brief": False,
    "modified": "2014-07-17T16:19:19.233Z",
    "preprocessed": True,
    "smallBusinessImpact": True,
    "pages": 1,
    "viewingStatus": "Unrestricted"
}
orig_id = "6018182002"

if __name__ == "__main__":
    filename = sys.argv[1]
    pages = json.load(open(filename))

    outdir = filename.split(".")[0]
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")
    splitter = re.compile("([^a-zA-Z0-9]+)")

    counter = 1
    for page in pages.itervalues():
        for row in page:
            # the first one is metadata
            parts = date_pattern.split(row[0])
            date_rcpt = dateutil.parser.parse(parts[1]).replace(tzinfo=dateutil.tz.tzutc()).replace(hour=12)
            out = {
                "id": "-".join([orig_id, str(counter)]),
                "applicant": parts[0].strip(),
                "dateRcpt": date_rcpt.isoformat()
            }
            out.update(orig_meta)

            # the actual comment starts in the second, separated by "Tell the FCC"
            comment = splitter.split(row[1].split("Tell the FCC")[-1].strip())
            for fragment in row[2:]:
                start = comment
                end = splitter.split(fragment.strip())

                s_word = start[-1]
                e_word = end[0]

                candidates = [s_word + e_word]
                if len(s_word) and len(e_word) and s_word[-1] == e_word[0]:
                    candidates.append(s_word + e_word[1:])

                # order candidates by length
                candidates = sorted(candidates, key=lambda c: len(c), reverse=True)

                valid_candidates = [c for c in candidates if c.lower() in most_common]

                # pick the first if any, otherwise combine with space
                if len(valid_candidates):
                    winner = valid_candidates[0]
                else:
                    winner = " ".join([s_word, e_word])

                comment = start[:-1] + [winner] + end[1:]

            merged_comment = "".join(comment)

            l_comment = fix_ligatures(merged_comment)

            out['text'] = l_comment

            print "Writing", counter
            
            path = os.path.join(outdir, "%s.json" % out['id'])
            outf = open(path, "w")
            json.dump(out, outf, indent=4)
            outf.close()

            counter += 1