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
		print word, keywords[word]

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

	print 'hi'
	article_results = []
	for article_dict in articles:
		
		article_result = dict()

		#
		url = 'http://www.bloter.net/archives/226384'
		article = Article(url)
		article.download()
		article.parse()
		


		#
		title ="HI"
		#title = article_dict['title']
		article.text = u"""인터넷에 위기가 닥쳤다는 말이 나온다. 인터넷 사용 환경이 모바일로 바뀌자 구글 같은 플랫폼 사업자는 사용자를 자사 서비스 안에 옭아매기 바쁘다. 페이스북은 콘텐츠 유통 채널을 넘어 스스로 인터넷이 되려는 꿈을 꾼다. 인터넷 보급율이 올라가는 한편에선 인터넷 개방성은 나날이 위협받는다.

한국에 인터넷을 처음 만든 이는 지금 같은 상황을 어찌 볼까. 전길남 박사(한국과학기술원 명예교수)를 만나 인터넷 위기론에 관해 물었다. 전길남 박사는 1982년 미국에 이어 세계에서 두 번째로 한국에 인터넷을 연결해낸 주인공이다. 지금 국내 IT 업계를 이끄는 많은 경영자를 길러낸 스승이기도 하다. 넥슨 창업자 김정주 NXC 대표, 네오위즈홀딩스 나성균 대표, ‘리니지’를 만든 XL게임즈 송재경 대표 등이 전길남 박사가 지휘한 시스템아키텍처연구실(SA랩)에서 공부했다.

전길남 박사는 전세계 인터넷 거버넌스 논의와 아시아의 역할부터 모바일 중심 시대의 숙제까지, 폭넓은 영역에 걸쳐 오랜 기간 쌓은 성찰을 드러냈다. 국내 대표 IT기업으로 꼽히는 삼성이 글로벌 경쟁력을 갖추려면 어떡해야 하는지 조언도 잊지 않았다. 인터뷰는 4월4일, 서울지역 한 카페에서 3시간여 동안 진행됐다.

안상욱 <블로터> 기자 : 만나서 영광이다. 3월에 필리핀 마닐라에서 열린 정보 인권 국제회의 ‘라이츠콘(RightsCON)’에 참석했다고 들었다. 라이츠콘에서 정보매개자에게 유통되는 정보에 관한 법적 책임을 물어서는 안 된다는 ‘마닐라 원칙’도 발표됐다. 그런데 한국에선 공공연히 정보매개자에게 책임을 묻는다. 한국 인터넷의 아버지로서 어떻게 봤는가.

[블로터포럼] “인터넷을 살찌우는 건 검열 아닌 투명성”
전길남 박사 : 한국이 인터넷 거버넌스 논의에서 소외됐다는 문제가 있다. 세계 인터넷 거버넌스 관련 정책을 보면 거의 90% 미국 학자 얘기다. 유럽에서 10%, 아시아, 아프리카, 라틴아메리카 등 다른 지역은 1% 뿐이다. 한국은 거의 0%다. 80년대에 인터넷을 시작했을 때부터 그랬다. 이러면 안 되겠다 싶어서 아시아 지역에서 논문 쓰고 책 내는 사람을 모아서 전세계 학자가 만나는 자리에 참여시키려고 한다.

전길남 박사 (한국과학기술원 KAIST 명예교수)
전길남 박사 (한국과학기술원 명예교수)
예를 들어 올해 10월 크리에이티브 커먼즈 코리아 10주년 행사에 요하이 뱅클러를 초대하려고 한다. 하버드 법대 교수인데 이 사람이 인터넷 거버넌스에 관해 쓴 논문은 세계 최고다. 그런데 이 사람을 한국에 초대하려면 문제가 생긴다. 비행기 타고 미국에서 오면 한국에 일주일은 머문다. 보통 우리 같은 연구자는 자기랑 비슷한 분야에서 책 쓰는 사람을 만나서 얘기하고 싶어한다. 그런데 국내에는 그런 책 쓰는 사람이 없다. 그래서 요하이 뱅클러 같은 인물이 여태껏 한국에 안 오는 거다. 와서 할 얘기가 없으니까.

그래도 오라고 할 거다. 요하이 뱅클러랑 로렌스 레식 같은 사람 몇명 초청하고 한국·중국·일본에서 최고라는 교수하고 묶어서 2~3시간 워크숍을 열 거다. 물론 힘들 거다. 그 자리에서 다 이해하길 기대하지는 않는다. 좋은 자극만 돼도 좋겠다.

안상욱 : 한국이 인터넷 거버넌스 논의에서 동떨어져 있다는 이야기에 공감한다. 어떻게 해야 한국이 제 역할을 할 수 있을까.

전길남 : 세계 추세라는 게 있다. 보통 미국이 주도한다. 그 다음은 유럽이다. 미국과 유럽이 협력하고 견제하면서 이끈다. 한국이나 다른 나라는 따라가는 셈이다. 이건 이것대로 쭉 가는 거고 한국은 한국대로 제대로 된 이슈를 밀어붙이는 거다. 오픈넷 같은 곳이 이런 역할을 톡톡히 해낸다. 2가지 논의가 공생하는 거다. 물론 갈등이 생길 수도 있다. 특히 한국이 이상한 방향으로 가는 나라 중 한 곳이라서 더 그렇다.

여기서 중요한 점은 지금 우리가 인터넷의 사회 기반 시설(인프라)을 만들 고 있다는 거다. 아무 것도 없던 곳에 기초를 다지고 있다. 지금 우리가 만드는 모든 결정은 일회용이 아니다. 앞으로 수십년 동안 인터넷이라는 세계의 기반이 된다. 그러니 더더욱 조심해야 한다.

빗대서 설명해보자. 지난 2년 동안 무슨 일이 있었는지 말해주겠다. 지금부터 800년 전에 영국에서 대헌장(마그나카르타)이 나왔다. 우리가 사는 근대 민주주의 사회가 여기서 시작됐다. 실제 세계에 대헌장이 있듯 인터넷에도 언젠가 그런 게 필요하다. 이걸 지난해 브라질에서 발표했다. 인터넷에서도 대헌장이 이제 막 시작한 거다. 대헌장이 민주주의를 얘기하는 시초이듯, 지금은 인터넷 거버넌스를 논의하는 극히 초창기다.

‘망 중립성’까지 법 테두리안에…브라질, 최초 인터넷 ‘인권보호’ 국가된다 <전자신문>
브라질, 인터넷 사용자 보호를 위한 권리장전 ‘마르코 시빌 다 인터넷’ 채택 <KISA>
라이츠콘에서 들어보니 브라질에서 영감을 받고 비슷한 걸 올해 프랑스와 이탈리아가 발표한다고 하더라. 정부와 시민단체가 같이 한다고 들었다. 그렇게 조금씩 움직이는 거다.

우리는 영국이 민주주의를 잘 가꿔왔다고 부러워한다. 마그나카르타부터 민주주의를 차근차근 잘 키웠는데 우리는 그렇게 못했다고 아쉬워한다. 우리는 영국처럼 자랑스러운 역사를 못 만들었다. 그럼 인터넷이라는 가상세계라도 제대로 만들 수 있으면 좋을텐데, 어렵다.

안상욱 : 라이츠콘에서 발표한 마닐라 원칙이 국내 인터넷 현실에 적지 않은 파장을 불러올 줄 알았는데 아무 언론도 다루지 않더라. <블로터>만 썼다. 인터넷 거버넌스는 관심조차 없는 게 아닌가 싶다.

전길남 : 그렇게 얘기하면 나도 해줄 말이 있다. 1982년 우리나라가 세계에서 두 번째로 인터넷을 연결했다. 3년 전이 한국 인터넷 30주년이었다. 그런데 인터넷을 처음 만들었을 때 어쨌는지 아나? 정부 평가에서 탈락이라더라. “왜 컴퓨터를 연결하는 데 신경 쓰냐. 컴퓨터나 제대로 만들어라” 이랬다. 정부에서 우리한테 준 프로젝트가 컴퓨터 국산화 프로젝트였으니까, 기본적으로 실패라는 얘기였다.

그때 내가 존경하는 선배가 컴퓨터 국산화와 네트워크를 따로 하지 말라고 조언했다. 두 프로젝트를 따로 하면 하나를 죽이기 쉬우니까 네트워크를 국산화 연구 속에 집어넣으라는 얘기였다. 사실 미국에서 처음 인터넷을 만들 때도 마찬가지였다. 알파넷 안에는 인공지능, 컴퓨터그래픽, 소프트웨어 공학 등 굉장히 많은 프로젝트가 있었다. 많은 사람이 각자 컴퓨터로 연구하다보니 그 컴퓨터를 연결할 필요가 생겼다. 이게 인터넷의 조상인 아르파넷 프로젝트다.

결국 연구를 주도하는 정부가 왜 컴퓨터를 연결해야 하는지 이해 못하니 안 되는 거다. 내가 너무 빨리 덤볐기 때문일지도 모른다. 10년 정도 늦게 했으면 훨씬 쉽게 됐을지도 모르지. 일찍 한다는 건 항상 어려울 수 있다.

안상욱 : 앞서 간다고 하니 이 말이 생각난다. 라이츠콘에서 한국 인터넷 규제가 상당히 앞섰다고 평가한다고 들었다. 인터넷 실명제 같이 말도 안 되는 규제를 정부가 내놓으니까 그에 발맞춰 시민단체도 다른 나라에서는 생각도 못한 부분을 두고 법원에서 싸우고 결국 세계에 유례가 없는 판례까지 이끌어낸다더라. 어떻게 생각하나.

전길남 : 비판적인 시각으로 보면 굉장히 발전되고 있다고 할 수 있다. 인터넷 실명제는 아무나 덤벼서 해결할 수 있는 문제가 아니었다. 김기창 교수 같이 유능한 사람이 마음 먹었으니 꽤 많은 일을 해낸 거다. 혼자 다 한 건 아니지만 굉장히 잘 했다.

안상욱 : 어이 없는 계기 때문이지만, 김기창 교수가 늘 주창해 온 액티브X와 공인인증서 철폐도 가시화되는 상황이다. 기형적인 한국 인터넷 환경이 오픈웹, 웹표준에 한발 더 다가가는 거다. 그런데 김기창 교수는 일선에서 물러서 요양 중인 걸로 보인다. 오랜 싸움에 지쳐서 그럴까.

전길남 : 보통 그정도로 일하면 3~4년은 쉰다. 영어로 ‘worn out’이라고 한다. 소모됐다, 지쳤다는 표현이다. 인터넷 벤처 사업하는 사람도 이런 사람 많다. 언제쯤 회복할 수 있을지는 모르겠다. 10년이 걸리는 사람도 있고 2·3년 만에 회복되는 사람도 있다.

김기창 교수는 본인을 위해서라도 몇 년은 아예 이런 일에서 손 떼고 쉬어야 한다. 다음에 완전히 괜찮아졌다고 털고 일어설 때까지 완전히 쉬어야 한다. 아직 젊잖나. 더 활동할 가능성이 있으니 5년이고 10년이고 쉬어도 된다. 쉬면서 생각도 정리하고 책도 쓰다가 또 활동하고 싶다면 다시 하면 된다. 지금 다시 한다고 하면 내가 말릴 거다. 아껴야 한다. 그 정도로 능력 있는 사람은 더 일해야 한다.

김기창 교수 같은 사람이 한 명 나오면 그 다음에도 계속 나온다. 물론 다른 사람이니 일하는 스타일은 다르겠지. 그래도 계속 나올 거다. 예를 들어 이번에 라이츠콘은 미국 전자프런티어재단(EFF)과 ICS, 한국 오픈넷 공동작업이다. 엑세스가 주도했지만 오픈넷도 잘 했다. 600명 정도가 참가했는데 한국 오픈넷더러 잘 한다고 하더라. 오픈넷이 주도한 세션만 10개 넘었다. 그런데 참가자가 몇 명이었는지 아나? 4명이었다. 그 정도면 잘 한거다.

안상욱 : 한국 인터넷 거버넌스 논의와 해외 온도차를 극복할 방안은 무엇일까.

전길남 : 분석을 잘 해야 한다. 이런 문제를 분석하는 논문도 나와야 한다. 이유는 이렇다. 인터넷이라는 건 굉장히 민주주의적인 개념이다. 한국에 민주주의가 정착한 건 문민정부가 들어설 때부터다. 이렇게 보면 한국에 민주주의가 들어온 지 얼마 안 된 거다. 20년 조금 넘은 거지. 그러니 실수도 하고 그런 거다. 영국이나 프랑스 같이 몇백년 민주주의해 본 나라와 같은 수준이길 요구하는 건 어렵다.

몇 년 만에 해결할 문제가 아니다. 가볍게 10년, 20년, 30년 매달려야 하는 작업이라고 생각하고 길게 가야 한다. 한국은 미국과 유사한 부분도 있고 다른 부분도 있다. 이런 걸 다 제대로 알고 가야 한다.

아직 아시아는 인터넷 담론을 소화하기 힘든 상황인지도 모르겠다. 미국과 유럽에서 인터넷 거버넌스 논의를 쏟아내는 건 경쟁이 붙었기 때문이다. 인터넷이 나온지 30년이 넘었고, 이제 거버넌스를 논의할 시기이니까 너나할 거 없이 다들 책 쓰는 거다. 5년 전에도 5년 후에도 못 쓴다. 지금이 제일 좋은 시기다. 하버드, MIT, 스탠포드 서로 경쟁한다. 영국도 그렇다. 우리는 이런 경쟁에 뛰어들 준비가 안 돼 있다.

“한국 학자도 인터넷 거버넌스 연구 나서야”

고민 중이다. 그렇다고 우는 소리만 하고 있으면 안 된다. 특히 나 같은 사람은 답을 내놓아야 한다. 30년 동안 내가 매달린 분야가 이쪽이니 아시아가 어떻게 해야 하는지 길을 제시하려고 노력하는 중이다.

나는 한국·일본·중국에서 좋은 논문을 쓰고 책을 쓰는 사람을 찾아내고 만들려고 한다. 지난 1~2년 동안 계속 가능성 있는 교수를 만나고 있다.

오늘 아침에도 우리나라에서 제일 잘 하는 사람을 야단쳤다. 한국어로 책 쓰지 말라고 했다. 영어로 쓰든지 아니면 한국말로 쓰되 누군가 번역할 만한 수준으로 쓰라고 했다. 간단한 문제다. 한국 인구는 5천만명인데 세계 인구는 70억명이다. 어느쪽을 대상으로 쓸 거냐. 그 책이 정말 중요한 작업이라면 대답할 필요도 없다. 보통 사람이라면 그냥 한국어로 열심히 쓰라고 하겠지. 하지만 우리나라 최고는 그러면 안 된다.

그 친구도 당황했을 거다. 자기는 나름대로 책 잘 쓴다고 생각했는데 내가 갑자기 말도 안되는 얘기를 하는 거잖나. 영어로 책 쓰는 게 얼마나 힘든데. 그래도 그렇게 해야 한다고 오늘 아침에 e메일 보냈다. 이렇게 해서라도 한국에서 제대로 된 책이 나와야 한다. 아시아에서 나오는 연구가 최소한 5%는 돼야 한다.

전길남 박사 (한국과학기술원 KAIST 명예교수)
전길남 박사 (한국과학기술원 KAIST 명예교수)
그 사이에 틈틈이 책도 쓴다. 1년에 한 권씩 책 쓴다. 책 쓰는 이유는 내가 죽기 전에 인터넷 시작에 대해 알고 있는 걸 남기기 위해서다. 세계에 나 같은 사람이 5~6명 될 거다. 내가 길 가다가 교통사고로 죽어버리면 큰 손실이다. 내 머리 속에 든 걸 다 잃어버리잖나. 그렇게 되지 않으려고 열심히 쓴다. 지금 안 기자와 인터뷰 하는 것도 그렇고.

사실 이번 주에 되게 기분 좋다. 역사적인 때다. 어제 아랍쪽에 인터넷 역사를 다룬 논문이 끝났다. 정확히 얘기하면 ‘서아시아와 북아프리카 인터넷의 역사(Internet History of West Asia and North Africa)’라고, 10페이지 정도 되는 논문이 끝났다.

미국 인터넷의 역사라고 하면 책도 있고 논문도 많다. 영국 인터넷의 역사도 자료 많다. 영국 사람이 얼마나 부지런하게 논문을 쓰는 사람인데. 그런데 아시아에서 인터넷 어떻게 시작했냐고 묻잖나? 내가 쓴 책이 2권 있다. 그 다음에 라틴아메리카, 아프리카에서 인터넷 어떻게 시작했는지 지역마다 써야 할 거고 한국은 한국 대로 쓰지. 인터넷이라는 게 워낙 큰 덩어리니까 지역마다 따로 써야 한다.

라틴아메리카는 내가 부탁하면 거절할 수 없는 사람에게 시켰다. 라틴아메리카에 인터넷 제일 처음 소개한 사람이 나다. 1987년 여름 런던인가 캠브리지에서 그 사람을 만났다. 브라질에서 왔다더라. 내가 그 사람한테 10월인가 11월에 미국 프린스턴에서 인터넷 콘퍼런스가 하니까 무조건 오라고 했다. 라틴아메리카 인터넷의 시작이다. 그 사람한테 논문 쓰라고 시키니, 나한테 못한다는 소리는 못 하잖나. 그렇게 중앙아프리카도 했다.

중동 쪽 사람이 없었다. 그래서 1~2년 정도 쓸 사람만 계속 찾았다. 2명 정도 쓰겠다고 나선 사람이 있는데 6개월쯤 지나니 도저히 못하겠다더라. 세계 전체로 봐도 항상 그 지역이 제일 마지막이다. 자료가 없는 동네라서 그렇다. 이슬람이 글을 잘 안 쓴다. 문화가 그런 듯하다. 그래서 누군가 해야 한다면 내가 해버리지 하고 마음먹었다. 어제 끝났다. 이제 세계 전지역을 커버했다. 제일 마지막 지역을 마무리했다는 게 중요하다. 이게 내가 쓰는 세 번째 책 일부분이 된다.

안상욱 : 모바일 시대가 도래하면서 열린 인터넷이 위협받는다는 지적이 나온다. 페이스북이나 구글 같은 플랫폼 사업자가 자사 플랫폼 안에 누리꾼을 묶어두는 통에 웹표준이 흔들리고 인터넷의 개방성이 앱의 폐쇄성으로 대체된다는 우려다. 한국 인터넷의 아버지로서 이런 상황을 어떻게 보는가?

전길남 : 모바일을 얘기할 때 화두가 3개 정도 있다. 안 기자가 말한 건 그 중에서 3번째 얘기 같다. 다른 3가지 사안에 비해 그렇게 중요한 사안은 아니다.

첫 번째 화두는 인터넷의 보편화다. 지금 세계 인터넷 인구가 30억명이 된다고 한다. 70억 인구 가운데 40% 정도 될 거다. 10년 안에 인터넷 사용자가 70억명, 지금보다 2배 이상 많아진다고 한다. 세계 인구 80~90%가 인터넷을 쓰게 된다는 얘기다. 10년 사이에 지금까지 나타난 사용자보다 더 많은 사람이 새로 유입된다. 이런 사람이 인터넷을 어떻게 쓰게 하느냐가 문제다.

인터넷이 새로 보급되는 곳은 거의 대부분 개발도상국이다. 이런 곳은 컴퓨터를 아예 안 쓴다. 모바일만 쓴다. 2가지 이유 때문이다. 유선망을 뛰어넘어 무선 인터넷망을 보급하는 게 첫 번째 이유다. 두 번째 이유는 돈이 없어서 스마트폰밖에 못 사기 때문이다. 개발도상국 가면 한 달 월급이 대충 10만원 정도 된다. 우리나라 말로 88만원 세대가 아니고. 10만원으로 PC와 스마트폰 2가지 제품을 어떻게 사겠나. 둘 중 하나만 사라고 하면 안 기자라면 뭘 고르겠나.

이마케터가 내놓은 인터넷 사용자 증가 전망(출처 : 이마케터)
▲이마케터가 내놓은 인터넷 사용자 증가 전망(출처 : 이마케터)
“인터넷 이용자, 2015년엔 30억명 돌파”
“인터넷 보급으로 개도국 토속어 멸종 위기”

안상욱 : 당연히 스마트폰이다. 이것만 있으면 웬만한 건 다 할 수 있잖나.

전길남 : 자네도 그렇잖나. 그렇게 되는 거다. 그런데 이런 사람이 인터넷을 접할 때는 영어를 쓸 가능성이 크다. 아프리카를 예로 들어보자.

아프리카에는 토속 언어가 2~3천개 정도 있다고 한다. 수십년 후에는 잘해야 하나 남을까. 나머지는 다 사라진다고 한다. 우리나라 사람한테 한글 쓸래 영어 쓸래 물어보면 한글 쓴다고 할 거다. 한글 워드프로세서가 있기 때문이다. 컴퓨터에서 한글을 쓸 방법이 없다면 한글을 쓸까. 또 한글로 검색할 정보도 있다. 그런데 토속어를 쓸 방법도 없고, 그 언어로 검색할 정보도 없다면 어떨까. 그러면 영어를 쓰겠지. 불행하게도 아프리카 사람이 영어를 잘 한다. 그러니까 계속 토속 언어가 사라진다. 토속 언어 입력기를 만들고 검색 시스템을 만들면 되지 않냐고 물을 수 있는데, 안 된다. 그냥 영어 쓰는 편이 훨씬 편한 탓이다.

하지만 영어는 영미권 사람이 쓸 때 완전한 시스템이다. 아프리카 사람에게 맞는 시스템은 아니다. 이런 문제는 어떻게 해결할 거냐는 게 중요한 문제다. 남은 시간이 10년 정도다. 길어봐야 10~20년 안에 해결해야 한다. 길을 찾지 못하면 20년 뒤에는 아프리카에서 수천개 언어가 다 사라진다. 이 언어가 생기는데 시간이 얼마나 걸렸을까. 하지만 인터넷처럼 파워풀한 게 있으면 없어지는 건 금방이다. 우리는 이 문제를 먼저 해결해야 한다.

안상욱 : 두 번째 문제는 무엇인가.

전길남 : 모바일과 데스크톱PC가 있었다. 노트북은 데스크톱에서 넘어간 개념이다. 노트북에서 모바일로 넘어가면 항상 손 뻗으면 닿을 거리에 기기가 있다. 몸에서 30~60cm 안에 있다. 밤에 잘 때도 그렇다. 24시간 접속 가능한 건 완전히 다른 환경이다. 그래도 괜찮은가. 생각해 볼 문제다.

항상 옆에 있는 게 편리한 점은 인정한다. 하지만 24시간 그렇게 해야 할까. 그렇게 하는 게 진짜로 우리 문화에 도움이 되는지는 다시 생각해 볼 문제다. 웨어러블은 모바일이 몸에 닿는 것과 마찬가지다. 24시간 지근거리에 있는 시스템을 어떤 식으로 적용할 거냐, 어떻게 하는 게 맞느냐라는 근본적인 문제를 검토해야 한다.

“유비쿼터스 환경, 사람에게 이득일까”

세 번째는 아까 안 기자가 얘기한 페이스북 구글 같이 앞서가는 회사가 어떻게 될 거냐는 얘기다. 페이스북을 예로 들어보자. 10년, 20년이 지나고도 페이스북이 있을까? 구글이 있을까? 마이크로소프트(MS)를 봐라. 20년 전에 MS가 지금처럼 되리라고 누가 짐작이라도 했나. 40년 전에는 IBM의 위치가 절대적이었다. 지금은 어떤가?

페이스북과 구글도 언제든지 한 번 크게 실수하면 무너진다. MS가 내일 당장 문 닫아도 크게 문제 되지는 않을 거다. MS 업적 중에 중요하다고 생각한 게 ‘오피스’였는데 지금은 구글 같은 데서 쓰면 그만이잖나. 그래서 이런 회사가 더 악착같이 생존하려고 노력하는 거다. 어떻게 하면 10년 뒤에 생존할지 위기의식을 갖고 일한다.

내가 보기엔 페이스북이 지닌 위험성은 PC 프로젝트라는 점이다. 페이스북은 모바일에 안 맞다. 컴퓨터 화면에 맞다. 그걸 억지로 모바일에 맞췄다. 다음에 누군가 모바일 환경에 꼭 맞는 시스템을 만들면 그때는 페이스북도 안 쓰게 될 거다. 주변 사람에게 오늘 카카오톡과 페이스북을 각각 몇 시간 썼는지 물어봐라. 카카오톡이 3시간 정도 된다면 페이스북은 30분 정도 될까? 이런 페이스로 2~3년 지나면 어떻게 되겠나. 페이스북을 가장 많이 쓰는 미국이 하루에 2시간 쓴다고 하더라. 한국과 일본에서는 그 시기가 벌써 지났다. 페이스북은 메인이 아니라 보조로 쓴다. 카카오톡, 라인이 페이스북 기능을 실으면 거기로 옮기면 그만이다.

그렇다고 페이스북이 내일모레 문 닫지는 않겠지. 어쩌면 굉장한 제품을 내놓아서 잘 될지도 모른다. 반대로 아예 망할 수도 있는 거고. 그런 면에서 구글이 좀 더 유리하다. 구글은 서비스가 많잖나. 유튜브는 아무도 견제 못 한다. 검색도 견제 안 된다. 그나마 한국에서 네이버 정도나 견제한다. 다른 나라에서는 못 한다.

“한국 온라인게임과 모바일 메신저는 세계 최고 수준”

안상욱 : 마지막 질문이다. 한국이 IT 강국이라고들 하는데 실상은 그렇지 못하다고 한다. IT 소비 강국일 뿐 제대로 된 글로벌 IT기업이 없다는 비판이다. 글로벌 기업이라고 해도 삼성 같은 대기업은 IT보다 제조업에 가깝다. 어떻게 해야 한국에서도 글로벌 IT 기업이 나올 수 있을까.

전길남 : 아니다. 문제 없다. 이미 한국에도 글로벌 IT 기업이 있다. 먼저 온라인게임. 이건 유저인터페이스(UI), 소프트웨어, 하드웨어가 복합된 어려운 분야다. 페이스북 같이 하나만 잘 해선 되는 게 아니다. 3가지 분야를 모두 다 잘해야 한다. 이걸 가장 잘 하는 곳이 넥슨, 엔씨소프트다. 두 회사는 세계 최고 경쟁력을 지녔다. 이들을 뛰어 넘을 회사가 세상이 없다. 왜 이걸 자꾸 무시하는지 이해가 안 간다. 물론 경쟁자는 있지만 UI와 소프트웨어 분야에서는 세계 최고다.

이 회사가 뭘 고민하는지 아나? 온라인에서 세계 최고가 됐다. 앞으로 5년, 10년, 15년 뒤를 목표가 뭐냐면 엔터테인먼트에서 세계 최고가 되는 거다. 오늘날 엔터테인먼트가 아니라 미래에 세계 최고가 될 수 있는지를 고민한다.

이때 경쟁자는 누구냐. 디즈니다. 극장에서 디즈니 영화 2시간 보면 느낌이 어떤가. 넥슨 게임 2시간하고 끝난 뒤 느낌은? 다르다. 디즈니가 잘 한다. 그런 경험에는 기꺼이 2시간을 쓸 수 있다. ‘온라인게임 할래, 디즈니 영화 볼래?’라는 질문에 질적인 차이가 있다. 이 간극을 극복할 방법을 고민하고 있다. 이 숙제를 푸는 사람이 디즈니가 지난 50년 동안 업계를 주도했듯 미래에 엔터테인먼트를 주도하는 사람이 될 거다. 이건 디즈니한테도 어려운 문제다.

사실 엔씨소프트와 넥슨을 합쳐서 미국 EA를 사버리고 싶었다. EA가 자기보다 큰 회사니까 혼자 사기는 힘들지만 두 회사가 합치면 살 수도 있잖나. 그래서 디즈니를 견제하자는 게 원래 아이디어였는데 성공은 못 했다. 그렇게 쉬운 일이 아니니까 안 될 수도 있다고 본다. 다들 내 제자니까 내가 특별히 도울 수 있는 건 없지만 잘 해보라고 응원은 한다.

전길남 박사가 2014년 5월27일 넥슨개발자콘퍼런스 NDC14 무대에 올라 게임 산업의 중요성을 강조했다. 제자인 넥슨 창업자 김정주 NXC 대표가 스승을 모신 자리였다.
전길남 박사가 2014년 5월27일 넥슨개발자콘퍼런스 NDC14 무대에 올라 게임 산업의 중요성을 강조했다. 제자인 넥슨 창업자 김정주 NXC 대표가 스승을 모신 자리였다.
전길남 박사 “게임은 SW 산업의 핵심”
두 번째로 지금 메신저 서비스 잘 한다. 카카오톡, 라인 말이다. 우리나라 사업 기반이 좋다. 하루에 제일 시간을 많이 쓰는 매체가 메신저다. 이 아이디어는 우리가 만든 거다. 미국 위챗이 규모는 크지만 아이디어는 한국에서 나왔다. 세계 최고 수준에서 업계를 주도한다. 이걸 앞으로 어떻게 할 거냐. 쇼핑을 붙일까 결제를 붙일까, 결사적으로 견제하고 있다.

2가지 분야에서 세계 최고 수준이면 되는 거 아닌가. 3개, 4개, 5개가 있으면 좋겠지만 오히려 1~2개라서 집중해서 할 수 있다. 애플, 구글, 페이스북을 견제하고 이기는 분야가 2가지 있다. 다른 나라 가봐라. 2가지 갖고 있는 나라 흔치 않다. 이 정도면 충분히 잘 하고 있는 거다. 언제낙 세 번째 분야를 개척해야겠지만 당장 중요한 일은 아니다.

물론 다들 문제는 안고 있다. 라인이 성공한 이유가 뭐라고 보나? 한국 밖에서 성공해서 한국으로 돌아왔기 때문이다. 성공하려면 한국을 떠나야 하는 문제를 먼저 해결해야 한다. 카카오톡은 굉장히 어려울 거 같다. 한국을 못 떠나기 때문이다. 우리만 이런 문제에 시달리는 건 아니다. 스카이프는 리투아니아, 핀란드에서 시작했는데 결국 자기 나라 떠나서 미국에서 성공했다. 우리만 가진 문제는 아니다. 그렇지만 해결할 아이디어는 있어야 한다.

“삼성의 경쟁력? 직원더러 이재용을 존경하는지 물어보라”

안상욱 : 삼성은 글로벌 IT기업으로 발돋움할 잠재력을 충분히 갖고 있는 것 같은데 아직도 제조업 수준을 뛰어넘지 못한다. 어떻게 해야 삼성이 걸출한 IT 기업으로 발전할 수 있을까.

전길남 : 구글러한테 물어봐라. 너희 사장 어떻게 생각하냐고. “굉장한 사람이다, 존경한다”라고 얘기할 거다. 삼성 사람한테 물어봐라. 너희 오너 어떻게 생각하나. 주식 투자 잘한다고 할 거다. 구글에서 일하는 사람이 래리 페이지를 존경하는 것처럼 삼성 직원이 이재용을 존경할까. 이런 게 없으면 조직의 마인드 자체가 달라진다.

이건희, 이재용한테 제일 중요한 게 뭐라고 보나. 계속 삼성 오너 자리를 지키는 게 목적이다. 젊은 사람한테 물어봐라. 계속 이건희, 이재용 부자가 삼성 회장 자리를 지킬 수 있게 결사적으로 노력하는 일에 협조하고 싶은 사람이 있는지.

삼성이 구글을 견제하려면 하나가 돼야 한다. 만일 삼성을 위해 이재용이 잘 못하면 파면시킬 수 있어야 한다. 구글 래리 페이지가 그 자리에서 일을 제대로 못하면 앞으로 그 자리에 있을 수 없다. 조직이 중요한가 사장이 중요한가. 사장이 중요한 조직이라면 아무도 거기서 일하고 싶지 않을 거다. 조직이 중요하다면 그 조직에 사장이 없는 편이 낫다고 하면 그 사람이 관둘 수 있어야 한다. 애플 팀 쿡도 그 없이 애플이 더 잘 된다고 하면 언제든지 그만둘 거다. 지금은 잘 하고 있으니 그 자리에 있는 거다. 삼성에 이런 일이 가능할까. 삼성, LG, 대한항공 다 그렇다. 결국 그런 수준 밖에 안 되는 거다.

개인적으로 이건희 회장이 굉장한 사람이라고 생각한다. 우리나라 회사가 세계 최고가 될 수 있다는 걸 증명한 사람이다. 이건희 회장 전에는 한국 회사가 세계에서 최고가 되는 건 불가능했다. 2·3·4등은 할 수 있었지만 1등은 못 했다. 그런데 삼성 이건희 회장이 그걸 해냈다. 스마트폰 시장 점유율에서 1등이 됐고, 반도체도 그렇다. 그러니까 삼성이 굉장하다고 생각한다.

하지만 이건희 회장이 차기 사장이 될 기회를 아들에게만 준다면, 그게 삼성의 한계일 거다. 스티브 잡스가 아들에게 사장 시키고 다른 사람은 그 자리 못 앉게 하면 애플이 지금 같은 회사가 될 수 없었을 거다. 삼성의 공은 한국 회사도 세계 최고가 될 수 있다는 점을 보여준 것이다. 이 정도로 삼성의 미션은 끝나면 된다. 앞으로 구글, 페이스북 같은 회사를 만들 수 있는지는 젊은 사람들 손에 달렸다."""
		
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








