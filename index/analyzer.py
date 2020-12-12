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

    audio_count = 0
    if len(history_messages) < 100:
        return 0
    for message in history_messages:
        if message.audio:
            audio_count += 1

    if audio_count < 5:
        return 0

    activity_status = time.time() - int(history_messages[-1].date)
    # ----------------------------
    density = 0
    activity = 1
    importance = 1
    members = 2
    # ----------------------------
    members_count = int(members_count)
    density_temp = audio_count / len(history_messages)
    one_month = 2_630_000
    activity_temp = activity_status / one_month  # a month in seconds!

    # ----------------------------
    if density_temp < 0.1 and density_temp > 0.05:
        density = 1
    elif density_temp < 0.2:
        density = 2
    elif density_temp < 0.3:
        density = 3
    elif density_temp < 0.4:
        density = 5
    elif density_temp > 0.39:
        density = 6
    # ----------------------------
    if activity_temp < one_month / 20:
        activity = 5
    elif activity_temp < one_month / 10:
        activity = 4
    elif activity_temp < one_month / 5:
        activity = 3
    elif activity_temp < one_month / 2:
        activity = 2
    # ----------------------------
    # use members as well to get more valid and initial files
    if members_count < 1000:
        members = 1
    elif members_count < 10_000:
        members = 1.2
    elif members_count < 30_000:
        members = 1.4
    elif members_count < 50_000:
        members = 1.6
    # ----------------------------

    score = float((activity * density * members) / 60)
    # print(f"ativity: {activity}\ndensity: {density}\nmembers: {members}\nscore: {score}"
    #       f"\nactivity_status: {activity_status}\nactivity_temp: {activity_temp} - {timedelta(days=30).seconds} - {timedelta(days=1).seconds}")
    if score > 0.69:
        importance = 5
    elif score > 0.49:
        importance = 4
    elif score > 0.39:
        importance = 3
    elif score > 0.19:
        importance = 2

    return importance
