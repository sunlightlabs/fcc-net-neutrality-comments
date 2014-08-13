import sys, os, json, shutil, operator

credo_dir = sys.argv[1].rstrip(os.path.sep)
full_dir = sys.argv[2].rstrip(os.path.sep)

def all_files(dir):
    return reduce(operator.add, [[os.path.join(x[0], y) for y in x[2]] for x in os.walk(dir)])

for path in sys.argv[1:]:
    for f in all_files(credo_dir):
        if f.endswith('.json'):
            of = os.path.join(*([full_dir] + f.split(os.path.sep)[-2:]))
            if "-" in os.path.basename(f):
                # copy to the data directory
                if not os.path.exists(of):
                    print "Copy %s to %s" % (f, of)
                    shutil.copy(f, of)
                else:
                    print "%s already exists" % of
            else:
                # delete from the data directory
                if os.path.exists(of):
                    print "Delete %s" % (of)
                    os.unlink(of)
                else:
                    print "%s already deleted" % of
    