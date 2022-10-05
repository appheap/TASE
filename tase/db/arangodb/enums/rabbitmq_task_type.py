from enum import Enum


class RabbitMQTaskType(Enum):
    UNKNOWN = "unknown"

    ADD_CHANNEL_TASK = "add_channel_task"
    CHECK_USERNAMES_TASK = "check_usernames_task"
    DUMMY_TASK = "dummy_task"
    EXTRACT_USERNAMES_TASK = "extract_usernames_task"
    INDEX_AUDIOS_TASK = "index_audios_task"
    SHUTDOWN_TASK = "shutdown_task"

    CHECK_USERNAMES_JOB = "check_usernames_job"
    DUMMY_JOB = "dummy_job"
    EXTRACT_USERNAMES_JOB = "extract_usernames_job"
    INDEX_AUDIOS_JOB = "index_audios_job"
