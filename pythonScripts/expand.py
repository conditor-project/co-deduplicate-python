#!/usr/bin/python3

import sys
import json
import os

parentDicrectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDicrectory)

import deduplicate.conf as conf  

## Decomment where you don't use the Web service
# corpus = json.load(sys.stdin)

# for data in corpus :
#     #data = json.loads(line)
#     record = conf.Record(data['value'])
#     dup = record.deduplicate()
#     data["value"] = dup
#     sys.stdout.write(json.dumps(data))
#     sys.stdout.write('\n')

for line in sys.stdin :
    data = json.loads(line)
    record = conf.Record(data['value'])
    dup = record.deduplicate()
    data["value"] = dup
    sys.stdout.write(json.dumps(data))
    sys.stdout.write('\n')
