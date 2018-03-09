# -*- coding: utf-8 -*-
import csv
import json
from konlpy.tag import Kkma
from collections import Counter
from operator import itemgetter
import itertools
import re, random
import urllib2
from bs4 import BeautifulSoup
from newspaper import Article
import newspaper
from konlpy.tag import Kkma
from konlpy.utils import pprint



#########
#       #
#########
def trim_sentences(sentences):

	# remove duplicates
	j = 0
	while ( j < len(sentences)):
		sentence = sentences[j]
		if sentence in sentences[j+1:]:
			sentences.remove(sentence)
		else :
			j += 1

	# split ▲ , -
	i = 0
	while ( i < len(sentences) ):
		sentence = sentences[i]

		if u'…' in sentence:
			temp = re.split(u'…', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])

		if u'. ' in sentence:
			temp = re.split(u'. ', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])

		if u'   ' in sentence:
			temp = re.split(u'   ', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])
		if u'▲' in sentence:
			temp = re.split(u'▲', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])
		if sentence.count(u'-') >= 2:
			temp = re.split(u'-', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])
		
		i += 1


	# merge_sentence
	i = 0
	while ( i < len(sentences)):
		sentence = sentences[i]	
		if len(sentence) < 10:
			if '.' in sentence[len(sentence)/2:] :
				if i > 0 :
					sentences[i-1] += sentence
					sentences.pop(i)
				else :
					i += 1	
			else :
				if i < (len(sentences) - 1 ):
					sentences[i+1] = sentence + sentences[i+1]
					sentences.pop(i)
				else :
					i += 1
		else :
			i += 1
	

	# split using http*.jpg
	i = 0
	while ( i < len(sentences) ):
		sentence = sentences[i]

		if u'http' in sentence and u'.jpg' in sentence:
			temp = re.split(u'http.*?\.jpg', sentences[i])
			if len(temp) > 1:
				sentences.pop(i)
				for j in range(0, len(temp)):
					sentences.insert(i+j, temp[j])
			i += len(temp)
		else :
			i += 1
	
	# remove [*] or some keywords
	i = 0
	while ( i < len(sentences)):
		if ( u'◀' in sentences[i] and u'▶' in sentences[i]):
			temp = re.split(u'◀.*?▶', sentences[i])		
			sentences[i] = ' '.join(temp).strip()		
		if u'글꼴 선택 본문 텍스트 크게 본문 텍스트 작게 스크랩' in sentences[i]:
			sentences[i] = sentences[i].replace(u'글꼴 선택 본문 텍스트 크게 본문 텍스트 작게 스크랩', '')
		if u'Copyrightⓒ 한국경제 TV. All rights reserved. (http: //www .wowtv .co .kr) 무단 전재 및 재배포 금지' in sentences[i]:
			sentences[i] = sentences[i].replace(u'Copyrightⓒ 한국경제 TV. All rights reserved. (http: //www .wowtv .co .kr) 무단 전재 및 재배포 금지', '')
		if u'+ - Tag Match < 저작권자 © 글로벌 이코노믹 무단 전재 및 재배포금지>' in sentences[i]:
			sentences[i] = sentences[i].replace(u'+ - Tag Match < 저작권자 © 글로벌 이코노믹 무단 전재 및 재배포금지>', '')			
		i += 1

	#
	i = 0
	while ( i < len(sentences)):

		if u'(' in sentences[i] and u')' in sentences[i] and u'뉴스':
			temp = re.split(u'\(.*뉴스.*?\)', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])

		if ( u'[' in sentences[i] and u']' in sentences[i]):
			temp = re.split(u'\[.*?\]', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])

		if u'(' in sentences[i] and u')' in sentences[i] and u'기자':
			temp = re.split(u'\(.*기자.*?\)', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])

		if u'기자' in sentences[i] and u'=' in sentences[i]:
			temp = re.split(u'기자.*?=', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])	

		if u'사진' in sentences[i] and u'=' in sentences[i]:
			temp = re.split(u'사진.*?=', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])		

		if u'특파원' in sentences[i] and u'=' in sentences[i]:
			temp = re.split(u'특파원.*?=', sentences[i])
			
			if len(temp) > 1:
				sentences[i] = temp[1]
				for j in range(2, len(temp)):
					sentences.insert(i+j-1, temp[j])		

		i += 1

	# remove null sentences
	i = 0
	while ( i < len(sentences)):
		sentence = sentences[i]

		if len(sentence.strip()) == 0 :
			sentences.pop(i)
		else :
			i += 1

	return sentences


def get_articles(url):

	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)

	news_as = soup.findAll('a', 'r_news_drw')

	articles = []
	for news_a in news_as:
		
		title = news_a.find('span', 'r_news_tit').get_text()
		press = news_a.find('em', 'r_press').get_text()
		news_img = news_a.find('img')
		img_url = None
		if news_img != None:
			img_url  = news_a.find('img')['src']
		url = news_a['href']

		article = dict()
		article['title'] = title
		article['press'] = press
		article['img_url'] = img_url
		article['url'] = 'http://m.news.naver.com' +url

		articles.append(article)

	return articles



def get_keyword_weight(kkma, sentences):
	
	def get_words(kkma, sentences):
		z = []
		for sentence in sentences:
			z.extend( word for word, t in kkma.pos(sentence) \
				if len(word) > 0 and ( t == 'NNG' or t == 'OL') ) 

		words = list(set(z))
		return words


	def get_matrix(kkma, words, sentences):

		word_index = dict()
		for j, word in enumerate(words) :
			word_index[word] = j

		word_matrix = [ [ 0 for j in range(len(words)) ] for i in range(len(words)) ]

		head_words = []
		for j, sentence in enumerate(sentences) :


			w = 1
			if i == 0:
				w = 2.128
			elif i == 1:
				w = 1.471
			elif i == 2:
				w = 1.220
			elif i == 3:
				w = 1.031
			elif i == 4:
				w = 1.031
			elif i == 5:
				w = 1.020

			"""
			w = 1
			if j == 0:
				w = 4
			elif j==1:
				w = 3
			elif j == 2:
				w = 2
			"""

			sentence_words = list(set([ word for word, t in kkma.pos(sentence) \
				if len(word) > 0 and ( t == 'NNG' or t == 'OL') ]))

			if j <= 3:
				head_words.extend(sentence_words)

			for a, b in itertools.permutations(sentence_words, 2):
				if word_index.get(a) != None and word_index.get(b) != None :
					word_matrix[word_index[a]][word_index[b]] += w
		

		for j in range(len(word_matrix)):
			row = word_matrix[j]
			s = sum(row) 
			if s > 0 :
				word_matrix[j] = [ 0.1 + 0.9 * float(e) / float(s) for e in row ]

			#print ' '.join([ str(e) for e in word_matrix[j]] )

		return word_matrix

	def get_eigen_vector(word_matrix_t):

		word_matrix = [ [ 0 for e in range(len(word_matrix_t))] for e in range(len(word_matrix_t)) ]
		for i in range(len(word_matrix_t)):
			for j in range(len(word_matrix_t)):
				word_matrix[i][j] = word_matrix_t[j][i]

		x = [ float(1) / float(len(word_matrix)) for i in range(len(word_matrix))]

		for j in range(100):
			y = [ sum((a * b) for a, b in itertools.izip(word_matrix[i], x)) for i in range(len(word_matrix))]
			x = [ e/sum(y) for e in y ]
			#print x

		return x

	#
	words = get_words(kkma, sentences)
	word_matrix = get_matrix(kkma, words, sentences)
	x = get_eigen_vector(word_matrix)
	word_weight = [ ( words[i], a ) for i, a in enumerate(x) ]
	word_weight = sorted(word_weight, key=itemgetter(1))
	
	keywords = dict([])
	weight_max = max( weight for word, weight in word_weight)
	weight_min = min( weight for word, weight in word_weight)
	for word, weight in word_weight:
		w = 1
		if weight_max != weight_min :
			w = (weight - weight_min) / (weight_max - weight_min) # * (weight / weight_max)	
		keywords[word] = w * w
		#print word, keywords[word]

	#
	"""
	c = Counter(z)
	a = [ ( word, c[word] )  for word in c if c[word] > 1 ]

	a = sorted(a, key=itemgetter(1), reverse=True)
	keywords = dict([])
	for word, c in a:
		keywords[word] = c * c
		print word, c
	"""


	"""
	z = []
	for sentence in sentences[:3]:
		z.extend( word for word, t in kkma.pos(sentence) \
			if len(word) > 1 and ( t == 'NNG' or t == 'OL') ) 
	z = list(set(z))

	z_last = []
	for sentence in sentences[3:]:
		z_last.extend([ word for word, t in kkma.pos(sentence) \
			if len(word) > 1 and ( t == 'NNG' or t == 'OL')])

	ratio = float(len([ word for word in z_last if word in z ])) / float(len(z_last))
	
	if ratio > 0.1 :
		for word in z :
			if keywords.get(word) != None:
				keywords[word] = keywords[word] * 2
	"""

	return keywords


#########
#       #
#########
def forasterisk_algorithm(sentences):

	def amplify_factor(sentence):
		sentence = sentence.replace(' ', '')
		f = 1
		if u'밝혔다' in sentence:
			f *= 1.1
		if u'확인됐다' in sentence:
			f *= 1.2
		if u'시작했다' in sentence:
			f *= 1.1
		if u'하고있다' in sentence:
			f *= 0.5
		if u'되고있다' in sentence:
			f *= 0.8
		if u'?' in sentence:
			f *= 0.6
		if u'나타났다' in sentence:
			f *= 1.2
		if u'모습을보이고있다' in sentence:
			f *= 0.8
		if u'멘붕' in sentence:
			f *= 0.6
		if u'하지만' in sentence:
			f *= 0.8
		if u'사진' in sentence and u'있다' in sentence:
			f *= 0.5
		if not u'.' in sentence:
			f *= 0.5
		if u'제공' in sentence and (u'왼' in sentence or u'오른' in sentence or u'위' in sentence or u'아래' in sentence):
			f *= 0.5
		return f

	# init
	kkma = Kkma()

	#
	keywords = get_keyword_weight(kkma, sentences)

	#
	max_i = -1;
	max_sentence = None;
	max_sum = -1;
	avg_sentence_len = float(sum(len(s) for s in sentences)) / float(len(sentences))
	for i, sentence in enumerate(sentences) :
		sentence_keywords = list(set([ word for word, t in kkma.pos(sentence) if len(word) > 0 and ( t == 'NNG' or t == 'VV' ) ])) 
		
		if len(sentence_keywords) == 0:
			continue
		
		w = 1
		if i == 0:
			w = 2.128
		elif i == 1:
			w = 1.471
		elif i == 2:
			w = 1.220
		elif i == 3:
			w = 1.031
		elif i == 4:
			w = 1.031
		elif i == 5:
			w = 1.020

		len_panelty = (len(sentence) - avg_sentence_len) * 0.25 + avg_sentence_len
		
		s = float(w) * sum(keywords[word] for word in sentence_keywords if keywords.get(word) != None) \
			/ len_panelty

		s *= amplify_factor(sentence)

		#print "-> ", i, s, len(sentence), len(sentence_keywords)
		if s > max_sum :
			max_sum = s
			max_i = i
			max_sentence = sentence
	
	#
	target_index = max_i
	#print max_sentence
	#print max_sum

	return target_index



"""

"""
def get_json():
	import json
	articles = get_articles('http://m.news.naver.com/')
	kkma = Kkma()
	article_results = []
	for article_dict in articles:
		
		article_result = dict()

		#
		article = Article(article_dict['url'])
		article.download()
		article.parse()
		
		#
		title = article_dict['title']
		text = article.text
		top_img_url = article.top_image

		print title
		print top_img_url

		#
		sentences = trim_sentences(kkma.sentences(text))
		target_index = forasterisk_algorithm(sentences)

		sentence = sentences[target_index].strip()
		print sentence

		article_result['title'] = title
		if article_dict['img_url'] != u'http://mimgnews2.naver.net/image/navernews_200x200_new.jpg':
			article_result['img_url'] = article_dict['img_url']
		article_result['sentence'] = sentence
		article_result['press'] = article_dict['press']
		article_result['url'] = article_dict['url']

		article_results.append(article_result)
	
	result = dict()
	result['articles'] = article_results

	return json.dumps(result)

###########################
# SCRIPT                  #
###########################
f = open("0.json", 'w') 
result = str(get_json())
f.write(result)
f.close()








