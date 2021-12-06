import re
from . import utils
from . import params

class RecordDeduplicate :
    def __init__(self, record, es, index) :
        self.record = record
        self.es = es
        self.index = index
        self.dupList = []
        self.result_field = ["deduplicateRules", "idConditor", "source", "sourceUid"]

    def preprocess(self, sent) :
        """
        split a sentence, remove stopwords and join token
        :param sentence : a sequence of tokens
        :return preprocessed sentence : sentence where stop word is removed
        """
        if not isinstance(sent, str) :
            sent = str(sent)
        tokens = [token for token in re.findall("\w+", sent) \
            if token not in params.titleStopwords]
        return " ".join(tokens)

    def query(self) :
        """
        For a given sentence, preprocess and query elastic
        :param sentence
        :return elasticsearch responses
        see https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html
        for details.
        """
        default_title = self.record['title']['default']
        req = self.preprocess(default_title)
        body = {
            'query': {
                'bool': {
                    'must': [
                        { 'match': {
                            'title.default': {
                            'query' : req,
                            'fuzziness': "AUTO",
                            'minimum_should_match': '60%'
                                }
                            }
                        }]
                        }
                    }
                }

        res = self.es.search(index = self.index, body = body)
        return res


    def deduplicate(self) :
        """
        Deduplicate function.
        :param record : bibliographic record
        :return duplicates if exists. duplicates are list of dict. each dict contains :
         - idConditor
         - source
         - sourceUid
         - decision
         - deduplicateRules
        """
        if not isinstance(self.record, dict) :
            return {"error" : {"code" : 104, "type" : "<class 'Type'>", "message" : "Must be an Object"}}

        if not bool(self.record):
            return {"error" : {"code" : 103, "type" : "<class 'ValueError'>", "message" : "Empty object"}}

        if "sourceUid" not in self.record :
            return {"error" : {"code" : 101, "type" : "<class 'KeyError'>", "message" : "KeyError('sourceUid')"}}

        # take idConditor for duplicates if exists
        duplicatesIdConditor = []
        try :
            duplicatesIdConditor = [x["idConditor"] for x in self.record["duplicates"]]
        except Exception as err :
            pass

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

                    dico["deduplicateRules"] = comp.duplicate_rules
                    dico['type'] = dupCandidateRecord["typeConditor"]
                    self.dupList.append(dico)

            return [x for x in self.dupList if x["sourceUid"] != self.record["sourceUid"]]
        else : return []
