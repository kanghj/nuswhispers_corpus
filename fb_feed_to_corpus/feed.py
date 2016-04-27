import requests
import json
from collections import defaultdict

with open('.config') as config_file:
    _ACCESS_TOKEN = json.load(config_file)['access_token']
    if not _ACCESS_TOKEN:
        raise ValueError('config file should be init with a user access token. '
                         'Get one from https://developers.facebook.com/tools/explorer ?')

    print("test if access token is valid")
    _test_req = requests.get('https://graph.facebook.com/v2.2/me?access_token=%s' % (_ACCESS_TOKEN, ))
    if _test_req.status_code != 200:
        print(_test_req)
        raise ValueError("Invalid access token? Get one from https://developers.facebook.com/tools/explorer " + str(_test_req.status_code) + ' received :' + _test_req.text)


def post_contents(feed):
    return map(lambda post: post['message'], feed['data'])


def post_contents_with_id(feed):
    result = defaultdict(lambda: "")

    for post in feed['data']:
        try:
            result[post['id']] = post['message']
        except KeyError as e:
            pass
    return result


def num_likes_of_each_post(feed):
    result = defaultdict(lambda: 0)
    for post in feed['data']:
        try:
            result[ post['id'] ] = len(post['likes']['data'])
        except KeyError:
            pass
    return result


def num_comments_of_each_post(feed):
    result = defaultdict(lambda: 0)
    for post in feed['data']:
        try:
            result[ post['id'] ] = len(post['comments']['data'])
        except KeyError:
            pass
    return result


def next_page(data):
    return json.loads(
        _feed_as_text_from_url(
            data['paging']['next']
        )
    )


def as_json(name):
    return json.loads(
        _feed_as_text(name)
    )


def _feed_as_text(name):
    return _feed_as_text_from_url(
        'https://graph.facebook.com/v2.2/%s/feed?access_token=%s'
        %
        (name, _ACCESS_TOKEN)
    )


def _feed_as_text_from_url(url):
    return requests.get(url) \
                   .text
