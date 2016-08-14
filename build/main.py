#! /usr/bin/env python3
from __future__ import ( division, absolute_import, print_function, unicode_literals)

if __name__ == "__main__":
    import main
    raise SystemExit(main.main())

import os, sys, tempfile, logging
import shutil
import subprocess
import tarfile

kTarbalsDir = "../toolchain/tarballs/"
kPatchesDir = "../toolchain/patches/"

class Tarbal:
    url = ""
    pk = ""
    desc = ""
    patchItem = ""

    def __init__(self, url, pk, desc, patchItem=""):
        self.url = url
        self.pk = pk
        self.desc = desc
        self.patchItem = patchItem

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

def downloadFile(url, saveTo):
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = saveTo + os.path.basename(path)

    with open(filename, 'wb') as f:
        meta = u.info()
        items = meta.items()
        item = [item for item in items if item[0].lower() == 'Content-Length'.lower()]
        headerName, metaLength = item[0]
        fileSize = None
        if metaLength:
            fileSize = int(metaLength)
        print("Downloading: {0} Bytes: {1}".format(url, fileSize))

        fileSizeDL = 0
        blockSize = 8192
        while True:
            buffer = u.read(blockSize)
            if not buffer:
                break

            fileSizeDL += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(fileSizeDL)

            if fileSize:
                status += "   [{0:6.2f}%]".format(fileSizeDL * 100 / fileSize)
            status += chr(13)
            print(status, end="")
        print()

def grabTarbal(tarbal):
    print("Pulling {0}".format(tarbal.desc))

    if os.path.exists(kTarbalsDir + tarbal.pk):
        print("Exists")
    else:
        downloadFile(tarbal.url + "/" + tarbal.pk, kTarbalsDir)


def unpackTarbal(tarbal):

    with tarfile.open(kTarbalsDir + tarbal.pk) as f:
        f.extractall(kTarbalsDir)

    print("Extracted {0}".format(tarbal.pk))

def prepare():

    if not os.path.exists(kTarbalsDir):
        os.mkdir(kTarbalsDir)

    tarbals = [
        Tarbal("http://www.netgull.com/gcc/releases/gcc-4.6.4", "gcc-core-4.6.4.tar.gz", "gcc", "gcc-4.6.4"),
        Tarbal("http://www.netgull.com/gcc/releases/gcc-4.6.4", "gcc-g++-4.6.4.tar.gz", "g++"),
        Tarbal("http://ftp.gnu.org/gnu/binutils", "binutils-2.22.tar.gz", "binutils", "binutils-2.22"),
        Tarbal("http://b.dakko.us/~klange/mirrors", "newlib-1.19.0.tar.gz", "newlib", "newlib-1.19.0"),
        Tarbal("http://download.savannah.gnu.org/releases/freetype", "freetype-2.4.9.tar.gz", "freetype", "freetype-2.4.9"),
        Tarbal("http://zlib.net", "zlib-1.2.8.tar.gz", "zlib"),
        Tarbal("http://b.dakko.us/~klange/mirrors", "libpng-1.5.13.tar.gz", "libpng", "libpng-1.5.13"),
        Tarbal("http://www.cairographics.org/releases", "pixman-0.26.2.tar.gz", "pixman", "pixman-0.26.2"),
        Tarbal("http://www.cairographics.org/releases", "cairo-1.12.2.tar.xz", "cairo", "cairo-1.12.2"),
        Tarbal("http://b.dakko.us/~klange/mirrors", "MesaLib-7.5.2.tar.gz", "mesa", "Mesa-7.5.2"),
        Tarbal("http://b.dakko.us/~klange/mirrors", "ncurses-5.9.tar.gz", "ncurses", "ncurses-5.9"),
        Tarbal("ftp://ftp.vim.org/pub/vim/unix", "vim-7.3.tar.bz2", "vim", "vim73")
    ]

# Download dependencies
    for tb in tarbals:
        grabTarbal(tb)

# Remove old depencencies tree
    upackedTarballs = os.listdir(kTarbalsDir)
    for dir in upackedTarballs:
        dir = os.path.abspath(kTarbalsDir + dir)
        if os.path.isdir(dir):
            shutil.rmtree(dir)

# Unpack newest tarbals
    for tb in tarbals:
        unpackTarbal(tb)

    for tb in tarbals:
        if tb.patchItem:
             subprocess.check_call(["patch", "-p1 < " + kPatchesDir + tb.patchItem + ".patch"])

def main():
    workDir = os.getcwd()
    print(workDir)

    prepare()


