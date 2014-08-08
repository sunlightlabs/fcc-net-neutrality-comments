import xmltodict, sys, collections, traceback, json

COL_HEIGHT = 261
LEFT_MARGIN = 52.8

PAGES = []
ROW_OFFSETS = None

def find_closest(offset):
    differences = [(abs(offset - r_offset), r_offset) for r_offset in ROW_OFFSETS]
    mindiff = min(differences, key=lambda x: x[0])
    return mindiff[1]

def _handle_page(_, page):
    print "Page", len(PAGES) + 1
    global ROW_OFFSETS
    if _[-1][0] == "page":
        words = collections.defaultdict(dict)

        if 'word' in page:
            page_words = page['word'] if isinstance(page['word'], list) else [page['word']]
            for word in page_words:
                if isinstance(word, dict):
                    words[float(word['@yMin'])][float(word['@xMin'])] = word.get('#text', "")
                else:
                    print "WEIRD WORD", word
                    raw_input()

        # if this is the first page, loop through again and find all the leftmost words to figure out where the rows are
        if not ROW_OFFSETS:
            offsets = []
            for word in page['word']:
                xmin = float(word['@xMin'])
                if abs(xmin - LEFT_MARGIN) < .2:
                    offsets.append(float(word['@yMin']))
            ROW_OFFSETS = sorted(offsets)

        # merge approximate rows into their actual nearest canonical rows
        merged_rows = collections.defaultdict(dict)
        for row in words.keys():
            closest = find_closest(row)
            merged_rows[closest].update(words[row])

        page = {}
        for row in sorted(merged_rows.keys()):
            row_words = sorted(merged_rows[row].items(), key=lambda w: w[0])
            phrase = " ".join([w[1] for w in row_words])
            page[row] = phrase

        PAGES.append(page)
    return True

def handle_page(_, page):
    try:
        return _handle_page(_, page)
    except:
        traceback.print_exc()
        raise

if __name__ == "__main__":
    filename = sys.argv[1]
    xmltodict.parse(open(filename), item_depth=4, item_callback=handle_page)

    page_groups = collections.defaultdict(dict)
    for pagenum, page in enumerate(PAGES):
        page_groups[pagenum % COL_HEIGHT][pagenum] = page

    print "Collating..."
    out = collections.OrderedDict()
    for groupnum in sorted(page_groups.keys()):
        pages = [page_item[1] for page_item in sorted(page_groups[groupnum].items(), key=lambda x: x[0])]
        mega_page = collections.defaultdict(list)
        for page in pages:
            for row in sorted(page.keys()):
                mega_page[row].append(page[row].replace(u"\u00a0", u" ").replace(u"\u2010", u"-"))

        page_out = []
        for row in sorted(mega_page.keys()):
            page_out.append(mega_page[row])
        
        out[groupnum] = page_out

    print "Writing output..."

    outfile = open(sys.argv[1].split(".")[0] + "-rearranged.json", "w")
    json.dump(out, outfile, indent=4)
    print "Done."