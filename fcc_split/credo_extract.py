import os, json, sys, operator, urllib, urllib2, subprocess, tempfile, multiprocessing
from pyquery import PyQuery as pq

def write_file(json_dir, old_meta, new_meta):
    meta = dict(old_meta)
    meta.update(new_meta)
    outf = open(os.path.join(json_dir, "%s.json" % meta['id']), "wb")
    json.dump(meta, outf, indent=4)
    outf.close()

def all_files(dir):
    return reduce(operator.add, [[os.path.join(x[0], y) for y in x[2]] for x in os.walk(dir)])

def process_json(json_file):
    print json_file
    meta = json.load(open(json_file))

    # find the pdfs
    json_dir = os.path.dirname(json_file)
    pdfs = [f for f in os.listdir(json_dir) if f.startswith(meta['id']) and f.endswith('.pdf')]

    # the first pdf can be used straight
    print "Extracting %s..." % pdfs[0]
    text = subprocess.Popen(['pdftotext', os.path.join(json_dir, pdfs[0]), '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    write_file(json_dir, meta, {'id': meta['id'] + '-1', 'text': text})

    # the second one needs to be split and re-OCR'ed
    # split
    print "Extracting pages..."
    png_dir = os.path.join(json_dir, meta['id'] + "_png")

    pages = sorted(os.listdir(png_dir), key=lambda f: int(f.split("-")[1].split(".")[0]))
    for i, page in enumerate(pages):
        print "Extracting %s (OCR)..." % page

        text = subprocess.Popen(['tesseract', os.path.join(png_dir, page), '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
        write_file(json_dir, meta, {'id': meta['id'] + '-' + str(i + 2), 'text': text})

if __name__ == "__main__":
    if sys.argv[1].endswith('.json'):
        process_json(sys.argv[1])
    else:
        json_files = [f for f in all_files(sys.argv[1]) if f.endswith('.json') and '-' not in os.path.basename(f)]
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map(process_json, json_files)
