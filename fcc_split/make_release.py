import os, sys, subprocess

tag = sys.argv[2]
os.chdir(sys.argv[1])
for f in os.listdir('.'):
    if os.path.isdir(f):
        tarball = "%s-%s.tar.gz" % (f, tag)
        subprocess.Popen(['tar', 'cvfz', tarball, f]).communicate()