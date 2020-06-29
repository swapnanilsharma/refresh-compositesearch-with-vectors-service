from elasticsearch import Elasticsearch
import sys
import requests
import logging
from healthcheck import HealthCheck
import ast
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(filename="flask.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

def howami():
    return True, "I am good"

health = HealthCheck(app, "/hcheck")
health.add_check(howami)


def connect2ES(ipAddress='localhost', port=9200):
    # connect to ES
    es = Elasticsearch([{'host': ipAddress, 'port': port}])
    if es.ping():
            app.logger.info(f"Connected to ES!")
    else:
            app.logger.info(f"Could not connect to ES!")
            sys.exit()
    return es
 
@app.route('/modifysettings',  methods=['POST'])
def modifysettings():
    ESServer = request.args.get('ESServer') or request.get_json().get('ESServer', '')
    es = connect2ES(ipAddress=ESServer)
	  # creating autocomplete analyzer
    b = {"analysis": {
                      "analyzer": {
                                    "advance_search_analyzer": {
                                                                 "type": "custom",
                                                                 "char_filter": ["html_strip"],
                                                                 "tokenizer": "standard",
                                                                 "filter": ["lowercase", "stop", "asciifolding", "snowball"]
                                                               },
                                    "autocomplete": {
                                                     "type": "custom",
                                                     "tokenizer": "standard",
                                                     "filter": ["lowercase", "autocomplete_filter"]

                                    }
                                  },
                        "filter": {
                                   "autocomplete_filter": {
                                                           "type": "edge_ngram",
                                                           "min_gram": 1,
                                                           "max_gram": 20,
                                                           "token_chars": ["letter", "digit", "whitespace", "punctuation", "symbol"]
                                                          }
                        }
                     }
        }
    es.put_settings(index='compositesearch', body=b)
    # add autocomplete filter to mapping of fields name, description and keywords
    b = {"properties": {
                        "description" : {
                                         "type" : "text",
                                         "fields" : {
                                                     "keyword" : {
                                                                  "type" : "keyword",
                                                                  "ignore_above" : 256
                                                                 }
                                                    },
                                        "analyzer": "autocomplete"
                                        },
                        "name" : {
                                         "type" : "text",
                                         "fields" : {
                                                     "keyword" : {
                                                                  "type" : "keyword",
                                                                  "ignore_above" : 256
                                                                 }
                                                    },
                                        "analyzer": "autocomplete"
                                        },
                        "keywords" : {
                                         "type" : "text",
                                         "fields" : {
                                                     "keyword" : {
                                                                  "type" : "keyword",
                                                                  "ignore_above" : 256
                                                                 }
                                                    },
                                        "analyzer": "autocomplete"
                                        }
                       }
        }
    es.indices.put_mapping(index='compositesearch', body=b)
    return jsonify("SETTINGS MODIFICATION SUCCESSFUL")

@app.route('/vectortoelastic',  methods=['POST'])
def vectoriseCompositesearch():
    ESServer = request.args.get('ESServer') or request.get_json().get('ESServer', '')
    vecServerEndpoint = request.args.get('vecServerEndpoint') or request.get_json().get('vecServerEndpoint', '')
    es = connect2ES(ipAddress=ESServer)
    es.indices.put_mapping(index='compositesearch', body={"properties": {"name_vector": {'type': 'dense_vector', 'dims': 512}}})
    es.indices.put_mapping(index='compositesearch', body={"properties": {"description_vector": {'type': 'dense_vector', 'dims': 512}}})

    total_docs = es.count(index='compositesearch').get('count', 0)
    ret = es.search(index='compositesearch', _source=True, size=total_docs)

    headers = {'Content-Type': 'application/json'}

    for doc in ret['hits']['hits']:
        if not doc['_source'].get('name_vector', False) and not doc['_source'].get('description_vector', False):
            name = doc['_source'].get('name', "")
            desc = doc['_source'].get('description', "")
            payload = {"searchString": [name, desc]}
            response = requests.post(url=vecServerEndpoint, headers=headers, json=payload)
            response = ast.literal_eval(response.text)
            app.logger.info(f"Document processed: {doc['_id']}")
            b = {"doc": {"name_vector": response[0], "description_vector": response[1]}}
            es.update(index="compositesearch", id=doc['_id'], body=b,)
    app.logger.info("Completed indexing....")
    app.logger.info("*********************************************************************************")
    return jsonify("VECTOR INDEXING SUCCESSFUL")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True)
