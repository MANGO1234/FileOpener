from os.path import isdir, isfile, expanduser, split, relpath, join, commonprefix, normpath
from os import listdir, sep, makedirs


def directory_files(path):
    fs = []
    path = expanduser(path)
    for f in listdir(path):
        fs.append((isdir(join(path, f)), f))
    return fs
