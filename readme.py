class UserCommentsAndLikesParserQ:
    result_data = [{
        'url': 'input_login',
        'data': {
            'link': "post_link",
            'numner_of_likes: 'get_number_of_likes',
            'comments_data': 'get_comments_data',
            'likers_data': 'get_likers_data'
            }
    }]

    get_comments_data = [{
        'sender_name': '',
        'sender_link': '',
        'date': '',
        'text': '',
        'sum_id': ''
    }]

    get_likers_data = [{
        'link': '',
        "name": ''
    }]


class ChannelPostParserQ:
    '''
    return list[dict]
    '''
    url: str = 'input login'
    data: list[dict] = [{
        'post_link': '',
        'number_of_likes': '',
        'number_of_comments': '',
        'body': '',
        'date': '',
    }]


class UserProfileParserQ:
    all_data: list[dict] = [{
        'login': 'input login'
        'age'
        'username'
        'last_online'
        'is_private'
        "photo_url"
        "number_of_friends"
        "number_of_photo"
        "number_of_video"
        "number_of_music"
        "number_of_groups"
        "number_of_games"
    }]
