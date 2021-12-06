#!/usr/bin/env python

import sys
import json
import os
import argparse
import dotenv
from deduplicate.connect2elastic import ES_request, Connection
from deduplicate.deduplicate import RecordDeduplicate

dotenv.load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument("docobject_string", type=str, nargs='?')
args = parser.parse_args()


URL =  os.getenv("URL")
INDEX = os.getenv("INDEX")
SIZE = os.getenv("SIZE")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")
HTTP_PROXY = os.getenv("HTTP_PROXY")
proxies = {"https" : HTTPS_PROXY, "http" : HTTP_PROXY}

# Instanciate elastic client and its request class
es = ES_request(
    es_url=URL,
    connection_class= Connection,
    proxies = proxies,
    size = SIZE
)
docObjects = json.loads(args.docobject_string)

for docObject in docObjects :
    record = RecordDeduplicate(docObject, es = es, index = INDEX)
    duplicate = record.deduplicate()
    if "error" in duplicate :
        sys.stderr.write(json.dumps(duplicate))
    else :
        sys.stdout.write(json.dumps(duplicate))
