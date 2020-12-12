import time

def channel_analyzer(history_messages, members_count):
    """
    DONE

    this function returns the existing_channels_handler_by_importance of each channel which is a score between [0-5] and calculated as follow:
        score = (activity * density * members) / 60
    :param history_messages: a list of 100 latest messages shared by the channel
    :param members_count: the number of channel's members
    :return: existing_channels_handler_by_importance: assigned number for each score calculated for each channel
    """
