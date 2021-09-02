
import os
from utils import NoticeComparison
from elasticsearch import RequestsHttpConnection
from elasticsearch import Elasticsearch
from params import titleStopwords
from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from langdetect import detect

from dotenv import load_dotenv
load_dotenv()


# Instaciantye langdetctor
fr = SnowballStemmer('french')
en = PorterStemmer()


# Set connection config

esUrl = os.environ.get("ES_URL", "http://localhost:9200")
index = os.environ.get("INDEX")
doc_type = os.environ.get("RECORD")
proxies = os.environ.get("PROXIES")
size =os.environ["RESPONSE_SIZE"]



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

        try :
            duplicatesIdConditor = [x["idConditor"] for x in self.record["duplicates"]]
            res = self.query()
            if not res['hits']['hits'] :
                return {'duplicates' : self.dupList}
            else :
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
            return {'duplicates' : self.dupList}
        except Exception as err :
            return {"error" : 100, "type" : err.__class__}


if __name__ == "__main__" :
    from time import time
    import json
    import sys

    filename = "/home/dago/Documents/TDM/sprint-6/co-near_dup/test.json"
    with open(filename) as f :
        datas = json.load(f)
    for data in datas:
        a = time()
        record = Record(data)
        dup = record.deduplicate()
        print(f"Time Elapsed {time() - a}")
        print(dup)
        print()



