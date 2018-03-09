# -*- coding: utf-8 -*-
import csv
from utils_newspaper import get_title_text
from konlpy.tag import Kkma
from newspaper import Article
import json

#########
#       #
#########
def is_answer(s, sentences_answer):
	for sentence in sentences_answer:
		if s in sentence:
			return True
	return False 

def get_title_text(url):
	article = Article(url, language='ko')
	article.download()
	article.parse()
	title = article.title
	text = article.text
	return title, text

#########
#       #
#########
kkma = Kkma()
with open('data_raw.tsv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
	for j, row in enumerate(spamreader):
		
		#
		f = open('database/%d.json' % j, "w")

		#
		url = row[0]
		title, text = get_title_text(url)
		sentences = kkma.sentences(text)
		answer_sentences = row[1:]

		#
		result = dict()
		result['url'] = url
		result['sentences'] = sentences
		result['title'] = title
		result['text'] = text
		result['answer_sentences'] = [ s for s in answer_sentences if len(s) > 0 ]

		#
		f.write(json.dumps(result))
		#

		f.close()
		