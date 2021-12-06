"""
This file allows to Set a connection when we must configure a proxy
"""
from elasticsearch import RequestsHttpConnection, Elasticsearch

# Elastic search requests using proxies
class Connection(RequestsHttpConnection):
    def __init__(self, *args, **kwargs):
        proxies = kwargs.pop('proxies', {})
        super(Connection, self).__init__(*args, **kwargs)
        self.session.proxies = proxies


def ES_request(es_url, connection_class, proxies, size) :
    return Elasticsearch(
        es_url,
        connection_class = connection_class,
        proxies = proxies,
        size = size
    )
