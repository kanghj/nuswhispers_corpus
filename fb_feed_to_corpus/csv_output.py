import traceback

import feed
import csv

NUM_PAGES = 3000


def lists_from_feed(json):
    result = []

    for i in xrange(NUM_PAGES):
        if 'error' in json:
            raise ValueError('api returned error!')

        posts = feed.post_contents_with_id(json)
        likes = feed.num_likes_of_each_post(json)
        comments = feed.num_comments_of_each_post(json)

        for id, message in posts.iteritems():
            num_likes = likes[id]
            num_comments = comments[id]

            result.append([id, message.encode('utf-8'), num_likes, num_comments])

        try:
            json = feed.next_page(json)
        except KeyError as e:
            break
        print json

    return result


if __name__ == "__main__":
    nuswhispers = feed.as_json('nuswhispers')

    try:
        data = lists_from_feed(nuswhispers)
    except Exception as e:

        traceback.print_exc()
        print e.message
        raise e

    with open('feed.csv', 'wb+') as opened:
        writer = csv.writer(opened, delimiter=',')
        writer.writerow(['id', 'post', 'num_likes', 'num_comments'])
        for row in data:
            writer.writerow(row)
