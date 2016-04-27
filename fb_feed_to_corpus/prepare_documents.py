import csv
import scipy
import numpy as np
import lda
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import textmining
from collections import defaultdict

import matplotlib.pyplot as plt


def mean_len(rows):
    lengths = lengths_of_posts(rows)
    return np.mean(lengths)


def lengths_of_posts(rows):
    return [
        len(nltk.tokenize.word_tokenize(row[1])) for row in rows
    ]


def doc_term_matrix(docs):
    tdm = textmining.TermDocumentMatrix()

    for doc in docs:
        tdm.add_doc(doc)
    return tdm


if __name__ == "__main__":
    import re
    with open('full.csv', 'rb') as opened:
        opened.readline()
        reader = csv.reader(opened, delimiter=',')

        rows = []
        url_pattern = re.compile('http(s)?://.*\.com')
        num_pattern = re.compile('\d+')
        for row in reader:
            row[1] = row[1].decode('utf-8').lower() \
                           .replace('http://www.nuswhispers.com/confession/', '') \
                           .replace('https://www.nuswhispers.com/confession/', '') \
                           .replace('www.nuswhispers.com/confession/', '')
            row[1] = url_pattern.sub('', row[1])
            row[1] = num_pattern.sub('', row[1])
            rows.append(row)

    print 'number of docs', len(rows)

    lengths = lengths_of_posts(rows)
    mean_length = mean_len(rows)

    print 'average length' , mean_len(rows)
    print 'stdev of length', np.std(lengths)

    docs = map(lambda x: x[1], rows)
    lemmatizer = WordNetLemmatizer()
    processed = []
    skipped = 0
    for doc in docs:
        tokens = nltk.tokenize.word_tokenize(doc)

        processed.append(
            ' '.join(
                [lemmatizer.lemmatize(word) for word in tokens if word not in stopwords.words('english') and len(word) > 3]
            )
        )

    print 'skipped ', skipped

    print processed
    dtm = doc_term_matrix(processed).rows()

    headers = dtm.next()
    print headers

    dtm = np.array(
        list(dtm)
    )

    print dtm.shape

    num_topics = 4
    model = lda.LDA(n_topics=num_topics, n_iter=2500, random_state=1)
    model.fit(dtm)

    topic_word = model.topic_word_
    print("type(topic_word): {}".format(type(topic_word)))
    print("shape: {}".format(topic_word.shape))

    n = 20
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(headers)[np.argsort(topic_dist)][:-(n + 1):-1]
        print('*Topic {}\n- {}'.format(i, ' '.join(topic_words)))

    doc_topic = model.doc_topic_
    print("type(doc_topic): {}".format(type(doc_topic)))
    print("shape: {}".format(doc_topic.shape))

    for n in range(10):
        topic_most_pr = doc_topic[n].argmax()
        print("doc: {} topic: {}\n{}...".format(n,
                                                topic_most_pr,
                                                docs[n][:70]))

    # use matplotlib style sheet
    try:
        plt.style.use('ggplot')
    except:
        # version of matplotlib might not be recent
        pass

    """
    f, ax = plt.subplots(num_topics, 1, figsize=(8, 6), sharex=True)
    for i, k in enumerate(range(num_topics)):
        ax[i].stem(topic_word[k, :], linefmt='b-',
                   markerfmt='bo', basefmt='w-')
        ax[i].set_xlim(-50, 4350)
        ax[i].set_ylim(0, 0.08)
        ax[i].set_ylabel("Prob")
        ax[i].set_title("topic {}".format(k))

    ax[num_topics - 1].set_xlabel("word")

    plt.tight_layout()
    plt.show()

    f, ax = plt.subplots(5, 1, figsize=(8, 6), sharex=True)
    for i, k in enumerate([1, 3, 4, 8, 9]):
        ax[i].stem(doc_topic[k, :], linefmt='r-',
                   markerfmt='ro', basefmt='w-')
        ax[i].set_xlim(-1, 21)
        ax[i].set_ylim(0, 1)
        ax[i].set_ylabel("Prob")
        ax[i].set_title("Document {}".format(k))

    ax[4].set_xlabel("Topic")

    plt.tight_layout()
    plt.show()
    """

    topic_writers = []
    topic_files = []
    for i in xrange(num_topics):
        file = open('topics_' + str(i) + '.csv', 'wb')
        topic_files.append(
            file
        )
        topic_writers.append(
            csv.writer(
                file,
                delimiter=','
            )
        )

    topic_contents = defaultdict(list)

    for i, row in enumerate(rows):
        topic_most_pr = doc_topic[i].argmax()
        topic_contents[topic_most_pr - 1].append([row[0], topic_most_pr, row[2], row[3]])

    for topic_num, topic_content in topic_contents.iteritems():
        writer = topic_writers[topic_num - 1]
        writer.writerow(['id', 'topic', 'likes', 'comments'])
        for content in topic_content:
            writer.writerow(content)

    with open('topics.csv', 'wb') as opened:
        writer = csv.writer(opened, delimiter=',')
        writer.writerow(['id', 'topic', 'likes', 'comments'])
        for i, row in enumerate(rows):
            topic_most_pr = doc_topic[i].argmax()
            #print topic_most_pr
            writer.writerow([row[0], topic_most_pr, row[2], row[3]])

    for f in topic_files:
        f.close()