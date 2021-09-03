#!/usr/bin/python3
#!/usr/bin/env/python
import sys
import json
import os
import argparse

parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDirectory)


from deduplicate.deduplicate import Record


parser = argparse.ArgumentParser()

parser.add_argument('--docobject_string', type=str)
args = parser.parse_args()

corpus = json.loads(args.docobject_string)

for data in corpus :
    record = Record(data)
    duplicate = record.deduplicate()
    sys.stdout.write(json.dumps(duplicate))
    sys.stdout.write('\n')
