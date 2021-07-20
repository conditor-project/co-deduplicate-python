#import requests
from .utils import NoticeComparison
from elasticsearch import RequestsHttpConnection
from elasticsearch import Elasticsearch
from .params import titleStopwords
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from langdetect import detect


# Instaciantye langdetctor
fr = SnowballStemmer('french')
en = PorterStemmer()


# Set connection config

esUrl = "http://vp-conditor-es.intra.inist.fr:9200/"
index = "records-202012"
doc_type = "record"
proxies = {'https': 'http://proxyout.inist.fr:8080/', "http" : 'http://proxyout.inist.fr:8080/'}
size = 100


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

    # def testConnection(self) :
    #     try : 
    #         return requests.get(self.esUrl).json()
    #     except Exception as e : 
    #         return e  

# Instaciate connection

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
        except : 
            duplicatesIdConditor = []

            
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
                                "comment" : comp.comment,
                            }
                        )

            return {'duplicates' : self.dupList}


if __name__ == "__main__" : 
    from time import time
    import json
    import sys

    filename = "test.json"
    with open(filename) as f : 
        datas = json.load(f)
    for data in datas: 
        a = time()
        record = Record(data)
        dup = record.deduplicate()
        print(f"Time Elapsed {time() - a}")
        print(dup)
        print()

        

