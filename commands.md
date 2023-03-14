# CREATE COLLECTION

```curl --request POST \
--url http://localhost:8983/api/collections \
--header 'Content-Type: application/json' \
--data '{
  "create": {
    "name": "techproducts",
    "numShards": 1,
    "replicationFactor": 1
  }
}'```

#-s 2 -rf 2 number of shards, number of replicas

# DEFINE A SCHEMA
```curl --request POST \
  --url http://localhost:8983/api/collections/techproducts/schema \
  --header 'Content-Type: application/json' \
  --data '{
  "add-field": [
    {"name": "name", "type": "text_general", "multiValued": false},
    {"name": "cat", "type": "string", "multiValued": true},
    {"name": "manu", "type": "string"},
    {"name": "features", "type": "text_general", "multiValued": true},
    {"name": "weight", "type": "pfloat"},
    {"name": "price", "type": "pfloat"},
    {"name": "popularity", "type": "pint"},
    {"name": "inStock", "type": "boolean", "stored": true},
    {"name": "store", "type": "location"}
  ]
}'```

# INDEX SOME DOCUMENTS
A single document can be indexed as:

curl --request POST \
--url 'http://localhost:8983/api/collections/techproducts/update' \
  --header 'Content-Type: application/json' \
  --data '  {
    "id" : "978-0641723445",
    "cat" : ["book","hardcover"],
    "name" : "The Lightning Thief",
    "author" : "Rick Riordan",
    "series_t" : "Percy Jackson and the Olympians",
    "sequence_i" : 1,
    "genre_s" : "fantasy",
    "inStock" : true,
    "price" : 12.50,
    "pages_i" : 384
  }'

Multiple documents can be indexed in the same request:

curl --request POST \
  --url 'http://localhost:8983/api/collections/techproducts/update' \
  --header 'Content-Type: application/json' \
  --data '  [
  {
    "id" : "978-0641723445",
    "cat" : ["book","hardcover"],
    "name" : "The Lightning Thief",
    "author" : "Rick Riordan",
    "series_t" : "Percy Jackson and the Olympians",
    "sequence_i" : 1,
    "genre_s" : "fantasy",
    "inStock" : true,
    "price" : 12.50,
    "pages_i" : 384
  }
,
  {
    "id" : "978-1423103349",
    "cat" : ["book","paperback"],
    "name" : "The Sea of Monsters",
    "author" : "Rick Riordan",
    "series_t" : "Percy Jackson and the Olympians",
    "sequence_i" : 2,
    "genre_s" : "fantasy",
    "inStock" : true,
    "price" : 6.49,
    "pages_i" : 304
  }
]'

A file containing the documents can be indexed as follows:

curl -H "Content-Type: application/json" \
       -X POST \
       -d @example/products.json \
       --url 'http://localhost:8983/api/collections/techproducts/update?commit=true'


# COMMIT THE CHANGES
After documents are indexed into a collection, they are not immediately available for searching. In order to have them searchable, a commit operation (also called refresh in other search engines like OpenSearch etc.) is needed. Commits can be scheduled at periodic intervals using auto-commits as follows.
curl -X POST -H 'Content-type: application/json' -d '{"set-property":{"updateHandler.autoCommit.maxTime":15000}}' http://localhost:8983/api/collections/techproducts/config

