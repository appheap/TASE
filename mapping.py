audio_files_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "chat_id": {
                "type": "long"
            },
            "chat_username": {
                "type": "keyword"
            },
            "message_id": {
                "type": "integer"
            },
            "file_id": {
                "type": "keyword"
            },
            "file_name": {
                "type": "text",
                "analyzer": "standard"
            }, "file_size": {
                "type": "integer"
            },
            "duration": {
                "type": "integer"
            },
            "performer": {
                "type": "text",
                "analyzer": "standard"
            },
            "title": {
                "type": "text",
                "analyzer": "standard"
            },
            "times_downloaded": {
                "type": "integer"
            },
            "caption": {
                "type": "text",
                "analyzer": "standard"
            },
            "copyright": {
                "type": "boolean"
            }
        }
    }
}
