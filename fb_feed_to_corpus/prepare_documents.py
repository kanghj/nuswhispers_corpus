import csv
import glob
import re

from itertools import izip

nuswhispers_url_pattern = re.compile('(https?://)?(www\.)?nuswhispers\.com.{1,5}confession/.{1,5}\d+?')

if __name__ == "__main__":
    topic_filepaths = glob.glob('./topics_*.csv')

    topic_csvs = []
    topic_readers = []

    topic_txts = []
    topic_validation_txts = []

    for topic_filepath in topic_filepaths:
        f = open(topic_filepath, 'rb')
        topic_csvs.append(f)
        topic_readers.append(
            csv.reader(f, delimiter=',')
        )

        txt_filepath = topic_filepath.replace('.csv', '.txt')
        f = open(txt_filepath, 'w')
        topic_txts.append(f)

        validation_filepath = txt_filepath.replace('.txt', '.validation')
        f = open(validation_filepath, 'w')
        topic_validation_txts.append(f)


    full_filepath = './full.csv'

    sentence_map = {}

    hash_pattern = re.compile('#\d+:?')

    with open(full_filepath, 'rb') as full_file:
        reader = csv.reader(full_file, delimiter=',')

        for id, sentence, _, __ in reader:
            sentence_map[id] = hash_pattern.sub(
                '',
                nuswhispers_url_pattern.sub(
                    '',
                    sentence
                )
            )
            print(sentence_map[id])

    for topic_reader, topic_txt, topic_validation_txt in izip(topic_readers, topic_txts, topic_validation_txts):
        for i, row in enumerate(topic_reader):
            is_validation = i % 5 == 0

            instance_id = row[0]
            sentence = sentence_map[instance_id]

            if is_validation:
                topic_validation_txt.write(sentence + '\n')
            else:
                topic_txt.write(sentence + '\n')

    for csv, txt, validation in izip(topic_csvs, topic_txts, topic_validation_txts):
        csv.close()
        txt.close()
        validation.close()




