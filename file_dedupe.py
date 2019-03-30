import os
import sys
import operator
from itertools import groupby
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import argparse

first = operator.itemgetter(0)


def log(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def ls_r(path):
    for root, _, files in os.walk(path, followlinks=True):
        for file in files:
            p = os.path.join(root, file)
            if os.path.islink(p):
                continue
            yield p


def _checksum(filename):
    blksize = os.stat(filename).st_blksize
    m = sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(blksize)
            if not data:
                break
            m.update(data)
    return m.hexdigest(), filename


def checksum(filenames):
    with ThreadPoolExecutor(max_workers=4) as e:
        sums = e.map(_checksum, filenames)
    return list(filter(lambda s: s[0] is not None, sums))


def link_to_master(master, pawns, dry_run):
    for p in pawns:
        m = os.path.relpath(master, os.path.dirname(p))
        if not dry_run:
            os.remove(p)
            os.symlink(m, p)
        log(p, '->', m)


def main(path, dry_run=True):
    pairs = sorted(checksum(ls_r(path)), key=first)
    for hash, grp in groupby(pairs, key=first):
        _, g = zip(*grp)
        if len(g) > 1:
            link_to_master(g[0], g[1:], dry_run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dedupe files based on checksum. Use symlinks to resolve dups.')
    parser.add_argument('path', help='an integer for the accumulator')
    parser.add_argument('--live', action='store_true', default=False, help='Actually commit changes to disk')
    args = parser.parse_args()
    main(args.path, not args.live)
