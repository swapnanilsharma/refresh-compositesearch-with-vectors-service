# refresh-compositesearch-with-vectors-service

### This API is for putting dense-vectors for specific fields into the Elastic Search

#### Commands to run
   - sudo docker-compose up -d

#### API contract: 
    - ENDPOINT: http://<server-ip-address>:2233/vectortoelastic
    - METHOD: POST
    - HEADER: {"Content-Type": "application/json"}
    - BODY: {"ESServer": "40.87.27.176", "vecServerEndpoint": "http://40.87.27.176:2222/getvector"}
    - RESPONSE STRUCTURE: "SUCCESS"
    
    - HEALTHCHECK ENDPOINT: http://<server-ip-address>:2233/hcheck
