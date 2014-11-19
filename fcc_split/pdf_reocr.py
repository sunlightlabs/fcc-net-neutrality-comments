from gevent import monkey; monkey.patch_all()

import os, sys, subprocess, multiprocessing, gevent, gevent.queue


def reocr(filename):
    name = sys.argv[1].split(".")[0]
    png_dir = "%s_png" % name
    txt_dir = "%s_txt" % name

    if not os.path.exists(png_dir):
        os.mkdir(png_dir)

        # do the split first
        subprocess.Popen(['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pnggray', '-r300', "-sOutputFile=%s/pdf-%00d.png".replace("%s", png_dir), filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()

    if not os.path.exists(txt_dir):
        os.mkdir(txt_dir)

    # then tesseract everything
    from Queue import Empty
    num_workers = multiprocessing.cpu_count()
    todo_queue = gevent.queue.JoinableQueue(num_workers)

    def worker(todo_queue):
        while True:
            try:
                page = todo_queue.get()
            except Empty:
                return

            print "Extracting %s (OCR)..." % page
            text = subprocess.Popen(['tesseract', page, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]

            page_outfile = open(page.replace(png_dir, txt_dir).replace(".png", ".txt"), "w")
            page_outfile.write(text)
            page_outfile.close()
            
            todo_queue.task_done()

    processes = []
    for i in range(num_workers):
        proc = gevent.spawn(worker, todo_queue)
        proc.start()
        processes.append(proc)

    pages = sorted(os.listdir(png_dir), key=lambda f: int(f.split("-")[1].split(".")[0]))
    for i, page in enumerate(pages):
        todo_queue.put(os.path.join(png_dir, page))

    todo_queue.join()

    for proc in processes:
        proc.kill()

    text_pages = sorted(os.listdir(txt_dir), key=lambda f: int(f.split("-")[1].split(".")[0]))

    outfile = open("%s.txt" % name, "w")
    for page in text_pages:
        infile = open(os.path.join(txt_dir, page))
        outfile.write(infile.read())
        infile.close()

        outfile.write("\n==========\n")

    outfile.close()

if __name__ == "__main__":
    reocr(sys.argv[1])