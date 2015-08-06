#!/usr/bin/env python
import sys
import os
from tempfile import mkdtemp
from shutil import rmtree, move
import zipfile

def clean(dir):
    rmtree(dir)

def clean(directory):
    rmtree(directory)

# help
if len(sys.argv) == 0 || sys.argv[1] == '-h':
    print "usage : merman.py file1.zip file2.zip [file3.zip, ...] ouput.zip"
    print "      converts all .zip manga files given in argument to a single one"
    print "      by appending to the first one the pictures of the others"
    sys.exit(0)

# parse our arguments
input_files = []
output_file = sys.argv.pop()
del sys.argv[0]
for arg in sys.argv:
    if os.path.isfile(arg):
        if zipfile.is_zipfile(arg):
            input_files.append(arg)
    else:
        print "The file {} is not a valid input file".format(arg)
        sys.exit(1)

if os.path.isfile(os.getcwd() + "/" + output_file):
    print "The output file already exists"
    sys.exit(1)

# initialize variables
index = 1
tmpdir = mkdtemp()
output_dir_name, _ = os.path.splitext(output_file)
output_dir = tmpdir + "/" + output_dir_name
os.mkdir(output_dir)
os.listdir(output_dir)

# do the actual work
for zip_file in input_files:
    # unzip the file
    try:
        fp = open(zip_file, 'rb')
        fz = zipfile.ZipFile(fp)
        for name in fz.namelist():
            fz.extract(name, tmpdir)
    except all:
        print 'The file {} is not a valid zip file'.format(zip_file)
        clean(tmpdir)
        sys.exit(1)
    current_dir = sorted(next(os.walk(tmpdir))[1])
    current_dir.remove(output_dir_name)
    if not current_dir:
        new_dir, _ = os.path.splitext(zip_file)
        del _
        os.mkdir(tmpdir + '/' + new_dir)
        current_dir = [new_dir]
        for image_file in next(os.walk(tmpdir))[2]:
            move(tmpdir + '/' + image_file, tmpdir + '/' + current_dir[0] + '/' + image_file)
    current_dir = current_dir[0]
    work_dir = tmpdir + "/" + current_dir
    # rename the images
    for image_file in sorted(os.listdir(work_dir)):
        _, ext = os.path.splitext(image_file)
        del _
        os.rename(work_dir + "/" + image_file, output_dir + "/" + str(index).zfill(6) + ext)
        index += 1
    # delete the directory
    rmtree(work_dir)

# to create a clean zip we need to go to the working directory
try:
    current_path = os.getcwd()
    os.chdir(tmpdir)
except OSError:
    print "The folder {} does not exist anymore".format(tmpdir)
    sys.exit(1)

# create the output zip
zout = zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED)
for r, d, f in os.walk(output_dir_name):
    for image_file in f:
        zout.write(os.path.join(r, image_file))
zout.close()

# go back to cwd
try:
    os.chdir(current_path)
except OSError:
    print "The folder {} does not exist anymore".format(current_path)
    sys.exit(1)

# move it to cwd and exit
move(tmpdir + "/" + output_file, current_path + "/" + output_file)
clean(tmpdir)
sys.exit(0)
