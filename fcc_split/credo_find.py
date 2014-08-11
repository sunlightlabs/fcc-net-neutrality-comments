import sys, os, json, shutil

datadir = os.path.dirname(sys.argv[1].rstrip(os.path.sep))
outdir = os.path.join(datadir, "credo_files")
if not os.path.exists(outdir):
    os.mkdir(outdir)

for path in sys.argv[1:]:
    print "=>", path
    path = path.rstrip(os.path.sep)
    files = os.listdir(path)
    
    path_outdir = os.path.join(outdir, os.path.basename(path))
    if not os.path.exists(path_outdir):
        os.mkdir(path_outdir)

    large_files = [f for f in files if os.path.getsize(os.path.join(path, f)) > 5000000]
    bonds_files = [f for f in large_files if "becky bond" in json.load(open(os.path.join(path, f)))['applicant'].lower()]

    for f in bonds_files:
        source = os.path.join(path, f)
        dest = os.path.join(path_outdir, f)
        print source
        shutil.copyfile(source, dest)
    