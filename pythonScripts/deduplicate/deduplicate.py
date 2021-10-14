import os
import sys
import json
# import pathlib
from elasticsearch import RequestsHttpConnection
from elasticsearch import Elasticsearch
from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from langdetect import detect
import dotenv


dotenv.load_dotenv()

from . import utils
from . import params


# Instaciantye langdetctor
fr = SnowballStemmer('french')
en = PorterStemmer()


# Set connection config
ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
INDEX = os.environ.get("INDEX")
DOC_TYPE = os.environ.get("RECORD")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
proxies = {"https" : HTTPS_PROXY, "http" : HTTP_PROXY}
SIZE = os.environ["RESPONSE_SIZE"]


# Elastic search requests using proxies
class Connection(RequestsHttpConnection):
    def __init__(self, *args, **kwargs):
        proxies = kwargs.pop('proxies', {})
        super(Connection, self).__init__(*args, **kwargs)
        self.session.proxies = proxies


def ES_request(es_url, connection_class, proxies, size) :
    return Elasticsearch(
        [es_url],
        connection_class = connection_class,
        proxies = proxies,
        size = size
    )

# Instanciate elastic client and its request class
es = ES_request(
    es_url=ES_URL,
    connection_class= Connection,
    proxies = proxies,
    size = SIZE
)


class Record :
    def __init__(self, record, es = es) :
        self.record = record
        self.es = es
        self.dupList = []
        self.result_field = ["deduplicateRules", "idConditor", "source", "sourceUid"]

    def myStemmer(self, sent) :
        lang = detect(sent)
        tokens = ([fr.stem(word) for word in sent.split()],[en.stem(word) for word in sent.split()])[lang == "fr"]
        return " ".join([x for x in tokens if x not in params.titleStopwords])

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

        res = self.es.search(index = INDEX, body = body)
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
        except Exception as err :
            return {"error" : {"code" : 100, "type" : err.__class__, "message" : err}}


        if "idConditor" in self.record :
            duplicatesIdConditor.append(self.record["idConditor"])

        res = self.query()

        if res["hits"] :
            for i, rc in enumerate(res["hits"]["hits"]) :
                dupCandidateRecord = rc["_source"]
                comp = utils.NoticeComparison(self.record, dupCandidateRecord)
                comp.run()
                if comp.result == 1 :
                    dico = {}
                    for field in self.result_field :
                        try :
                            dico[field] = dupCandidateRecord[field]
                        except : pass

                    dico["deduplicateRules"] = comp.comment
                    dico['type'] = dupCandidateRecord["typeConditor"]
                    self.dupList.append(dico)

            return [x for x in self.dupList if x["sourceUid"] != self.record["sourceUid"]]
        else : return []
