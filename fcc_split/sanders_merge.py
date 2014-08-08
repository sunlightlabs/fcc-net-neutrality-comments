import re, json, sys

_ligatures_dict = dict(json.load(open("sanders_ligatures.json")))
_ligatures_re = re.compile("(%s)" % "|".join(map(re.escape, _ligatures_dict.keys())), flags=re.I)
def fix_ligatures(text):
    return _ligatures_re.sub(lambda mo: _ligatures_dict[mo.string[mo.start():mo.end()].lower()], text)

if __name__ == "__main__":
    filename = sys.argv[1]
    pages = json.load(open(filename))

    for page in pages.itervalues():
        for row in page:
            frow = " ".join(row)
            fixed = fix_ligatures(frow)
            if fixed != frow:
                print frow
                print fixed
