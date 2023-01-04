from enum import Enum


class RabbitMQTaskType(Enum):
    UNKNOWN = "unknown"

    ADD_CHANNEL_TASK = "add_channel_task"
    CHECK_USERNAME_TASK = "check_username_task"
    DUMMY_TASK = "dummy_task"
    EXTRACT_USERNAMES_TASK = "extract_usernames_task"
    INDEX_AUDIOS_TASK = "index_audios_task"
    SHUTDOWN_TASK = "shutdown_task"
    FORWARD_MESSAGE_TASK = "forward_message_task"

    CHECK_USERNAMES_JOB = "check_usernames_job"
    CHECK_USERNAMES_WITH_UNCHECKED_MENTIONS_JOB = "check_usernames_with_unchecked_mentions_job"
    DUMMY_JOB = "dummy_job"
    FORWARD_AUDIOS_JOB = "forward_audios_job"
    EXTRACT_USERNAMES_JOB = "extract_usernames_job"
    INDEX_AUDIOS_JOB = "index_audios_job"
    COUNT_AUDIO_INTERACTIONS_JOB = "count_audio_interactions_job"
    COUNT_PUBLIC_PLAYLIST_INTERACTIONS_JOB = "count_playlist_interactions_job"
    COUNT_HITS_JOB = "count_hits_job"
