# refresh-compositesearch-with-vectors-service

## This API is for creating modified mapping/settings of COMPOSITESEARCH index and putting dense-vectors for specific fields into the Elastic Search

### ElasticSearch and Kibana install:

 - sudo docker run -m 6G -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --name myelastic docker.elastic.co/elasticsearch/elasticsearch:7.7.0 &
 - sudo docker pull docker.elastic.co/kibana/kibana:7.7.1
 - sudo docker run --link <container_id>:elasticsearch -p 5601:5601 docker.elastic.co/kibana/kibana:7.7.1 &


#### Commands to run
   - sudo docker-compose up -d

#### API contract: 
    - ENDPOINT: http://<server-ip-address>:2233/addsettings
    - METHOD: POST
    - HEADER: {"Content-Type": "application/json"}
    - RESPONSE STRUCTURE: "SUCCESS"
    
    - elasticdump --input=http://110.0.0.9:9200/compositesearch --output=http://52.172.51.143:9200/compositesearch
    
    - ENDPOINT: http://<server-ip-address>:2233/vectortoelastic
    - METHOD: POST
    - HEADER: {"Content-Type": "application/json"}
    - BODY: {"ESServer": "40.87.27.176", "vecServerEndpoint": "http://40.87.27.176:2222/getvector"}
    - RESPONSE STRUCTURE: "SUCCESS"
    
    - HEALTHCHECK ENDPOINT: http://<server-ip-address>:2233/hcheck

