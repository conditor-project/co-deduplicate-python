#!/usr/bin/python3

import sys
import json
import os
import argparse

parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDirectory)

parser = argparse.ArgumentParser()

parser.add_argument('docobject_string', type=str)
args = parser.parse_args()

import deduplicate.conf as conf

corpus = json.loads(args.docobject_string)

for data in corpus :
    record = conf.Record(data)
    dup = record.deduplicate()
    data = dup
    sys.stdout.write(json.dumps(data))
    sys.stdout.write('\n')
