"""
audio_files_mapping mapper is the template for storing audio-file data in Elasticsearch database.
Featured fields:
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

"""
user_mapping mapper is the template for storing user data in Elasticsearch database.
Featured fields:
    1. First name
    2. Username
    3. Date joined
    5. Downloaded audio id list
    6. Downloaded audio count
    7. Lang code (Language code)
    8. Limited (is limited)
    9. Role
    10. Coins
    11. Last active date
    12. Is admin
    13. Sex (gender)
    14. Country
    15. Other
"""
user_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "first_name": {
                "type": "keyword"
            },
            "username": {
                "type": "keyword"
            },
            "date_joined": {
                "type": "integer"
            },
            "downloaded_audio_id_list": {
                "type": "keyword"
            },
            "downloaded_audio_count": {
                "type": "integer"
            },
            "lang_code": {
                "type": "keyword"
            },
            "limited": {
                "type": "boolean"
            },
            "role": {
                "type": "keyword"
            },
            "coins": {
                "type": "integer"
            },
            "last_active_date": {
                "type": "integer"
            },
            "is_admin": {
                "type": "boolean"
            },
            "sex": {
                "type": "keyword"
            },
            "country": {
                "type": "keyword"
            },
            "other": {
                "type": "text"
            }
        }
    }
}

"""
channel_mapping is the template for storing channel data in Elasticsearch database.
Featured fields:
    1. Title
    2. Username
    3. Importance
    4. Indexed from audio count
    5. Last indexed offset date
    6. Downloaded from count
"""
channel_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "keyword"
            },
            "username": {
                "type": "keyword"
            },
            "importance": {
                "type": "integer"
            },
            "indexed_from_audio_count": {
                "type": "integer"
            },
            "last_indexed_offset_date": {
                "type": "integer"
            },
            "downloaded_from_count": {
                "type": "integer"
            }
        }
    }
}

"""
channel_mapping is the template for storing channels-that-are-going-to-be-indexed data in Elasticsearch database.
"""
to_index_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {

        }
    }
}

"""
admin_log_control_mapping is the template for storing admin log data in Elasticsearch database.
Contains:
    1. Last offset date
    2. Members' count
"""
admin_log_control_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "last_offset_date": {
                "type": "integer"
            },
            "members_count": {
                "type": "integer"
            }
        }
    }
}

"""
user_list_mapping is the template for storing admin log data in Elasticsearch database.
Contains:
    1. Downloaded audio id list
    2. Playlists
"""
user_list_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "downloaded_audio_id_list": {
                "type": "keyword"
            },
            "playlists": {
                "type": "keyword"
            }
        }
    }
}


"""
playlist_mapping is the template for storing playlist data in Elasticsearch database.
Contains:
    1. Author id
    2. Title
    3. Description
    4. List
"""
playlist_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "author_id": {
                "type": "keyword"
            },
            "title": {
                "type": "text"
            },
            "description": {
                "type": "text"
            },
            "list": {
                "type": "keyword"
            }
        }
    }
}
