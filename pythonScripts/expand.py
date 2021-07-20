#!/usr/bin/python3

import sys
import json
import os
import argparse

parentDicrectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDicrectory)

parser = argparse.ArgumentParser()

parser.add_argument('--file', '-f', type=str, required=True)
args = parser.parse_args()

import deduplicate.conf as conf

fd = open(args.file, mode='r', encoding='utf8')
corpus = json.load(fd)

for data in corpus :
    record = conf.Record(data)
    dup = record.deduplicate()
    data = dup
    sys.stdout.write(json.dumps(data))
    sys.stdout.write('\n')

fd.close()
