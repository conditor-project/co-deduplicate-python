import os
import sys
import json
import pathlib
from elasticsearch import RequestsHttpConnection
from elasticsearch import Elasticsearch
from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from langdetect import detect

# Set path for importing deduplicate module
parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDirectory)

from deduplicate.utils import NoticeComparison
from deduplicate.params import titleStopwords


# Load envrionment variables
from dotenv import load_dotenv
load_dotenv()


# Instaciantye langdetctor
fr = SnowballStemmer('french')
en = PorterStemmer()


# Set connection config
esUrl = os.environ.get("ES_URL", "http://localhost:9200")
index = os.environ.get("INDEX")
doc_type = os.environ.get("RECORD")
proxies = json.loads(os.environ.get("PROXIES"))
size = os.environ["RESPONSE_SIZE"]


# Elastic search requests using proxies
class MyConnection(RequestsHttpConnection):
    def __init__(self, *args, **kwargs):
        proxies = kwargs.pop('proxies', {})
        super(MyConnection, self).__init__(*args, **kwargs)
        self.session.proxies = proxies


class ESRequest() :
    def __init__(self, esUrl = esUrl, index = index, proxies = proxies, size = size) :
        self.esUrl = esUrl
        self.index = index
        self.proxies = proxies
        self.es = Elasticsearch(
            [self.esUrl],
            connection_class = self.Connection,
            proxies = proxies,
            size = size
        )

    class Connection(MyConnection) :
        pass


# Instanciate elastic client and its request class
esr = ESRequest()
es = esr.es

class Record :
    def __init__(self, record, es = es) :
        self.record = record
        self.es = es
        self.dupList = []

    def myStemmer(self, sent) :
        lang = detect(sent)
        tokens = ([fr.stem(word) for word in sent.split()],[en.stem(word) for word in sent.split()])[lang == "fr"]
        return " ".join([x for x in tokens if x not in titleStopwords])

    def query(self) :
        titleDefault = self.record['title']['default']
        req = self.myStemmer(titleDefault)
        body = {
            'query': {
                'bool': {
                    'must': [
                        { 'match': {
                            'title.default': {
                            'query' : req,
                            'fuzziness': "AUTO",
                            'minimum_should_match': '70%'
                                }
                            }
                        }]
                        }
                    }
                }

        res = self.es.search(index =index, body = body)
        return res


    def deduplicate(self) :
        if not isinstance(self.record, dict) :
            return {"error" : {"code" : 104, "type" : "<class 'Type'>", "message" : "Must be an Object"}}

        if not bool(self.record):
            return {"error" : {"code" : 103, "type" : "<class 'ValueError'>", "message" : "Empty object"}}

        if "idConditor" not in self.record :
            return {"error" : {"code" : 102, "type" : "<class 'KeyError'>", "message" : "KeyError('idConditor')"}}

        if "sourceUid" not in self.record :
            return {"error" : {"code" : 101, "type" : "<class 'KeyError'>", "message" : "KeyError('sourceUid')"}}


        try :
            duplicatesIdConditor = [x["idConditor"] for x in self.record["duplicates"]]
            duplicatesIdConditor.append(self.record["idConditor"])
            res = self.query()

            for i, rc in enumerate(res["hits"]["hits"]) :
                dupCandidateRecord = rc["_source"]
                comp = NoticeComparison(self.record, dupCandidateRecord)
                comp.run()
                if comp.result == 1 :
                    if dupCandidateRecord['idConditor'] not in duplicatesIdConditor :
                        self.dupList.append(
                            {
                                "idConditor" : dupCandidateRecord['idConditor'],
                                "sourceUid" : dupCandidateRecord['sourceUid'],
                                "type" : dupCandidateRecord['typeConditor'],
                                "source" : dupCandidateRecord['source'],
                                "deduplicateRules" : comp.comment,
                            }
                        )
            return self.dupList
        except Exception as err :
            return {"error" : {"code" : 100, "type" : err.__class__, "message" : err}}

if __name__ == "__main__" :
    from time import time
    import json
    import sys

    # Set path for importing deduplicate module
    parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, parentDirectory)

    filename = os.path.join(parentDirectory, "tests/test.json")
    print(filename)
    with open(filename) as f :
        datas = json.load(f)
    for data in datas:
        a = time()
        record = Record(data)

        dup = record.deduplicate()
        print(f"Time Elapsed {time() - a}")
        print(data["idConditor"])
        print(dup)
        print()


