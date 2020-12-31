
"""
audio_files_mapping mapper is the template for storing audio-file data in Elasticsearch database.
It contains:
    1. Chat id
    2. Chat username
    3. Message_id
    4. File_id
    5. File_name
    6. File_size
    7. Duration
    8. Performer
    9. Title
    10. Times_downloaded
    11. Caption
    12. Copyright
"""
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
            },
            "file_size": {
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
