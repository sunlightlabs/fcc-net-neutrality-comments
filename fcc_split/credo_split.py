import os, json, sys, operator, urllib, urllib2, subprocess, tempfile, shutil, multiprocessing
from pyquery import PyQuery as pq

def all_files(dir):
    return reduce(operator.add, [[os.path.join(x[0], y) for y in x[2]] for x in os.walk(dir)])

def process_json(json_file):
    print json_file
    meta = json.load(open(json_file))

    # find the pdfs
    json_dir = os.path.dirname(json_file)
    pdfs = [f for f in os.listdir(json_dir) if f.startswith(meta['id']) and f.endswith('.pdf')]

    # the first pdf can be used straight
    text = subprocess.Popen(['pdftotext', os.path.join(json_dir, pdfs[0]), '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    print text

    # the second one needs to be split and re-OCR'ed
    # split
    print "Extracting pages...",
    png_dir = os.path.join(json_dir, meta['id'] + "_png")
    if not os.path.exists(png_dir):
        os.mkdir(png_dir)

    subprocess.Popen(['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pnggray', '-r300', "-sOutputFile=%s/pdf-%00d.png".replace("%s", png_dir), os.path.join(json_dir, pdfs[1])], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    print "done."

if __name__ == "__main__":
    if sys.argv[1].endswith('.json'):
        process_json(sys.argv[1])
    else:
        json_files = [f for f in all_files(sys.argv[1]) if f.endswith('.json') and '-' not in os.path.basename(f)]
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map(process_json, json_files)