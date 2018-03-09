# -*- coding: utf-8 -*-
from newspaper import Article
import newspaper
from konlpy.tag import Kkma
from konlpy.utils import pprint

kkma = Kkma()
cnn_paper = newspaper.build('http://joongang.joins.com/list/news/news_list.html?cloc=joongang|home|navi2')
for article in cnn_paper.articles:

	print '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	print article.url

	title, text = get_title_text(article.url)
	sentences = kkma.sentences(text)
	if len(sentences) == 0:
		continue
	
	print title
	print sentences[0]
	print text[:100]

#kkma = Kkma()
#nouns = kkma.nouns(text)
#pprint(kkma.nouns(text))

#print len(nouns)
#print len(set(nouns))

#'http://www.daejonilbo.com/news/newsitem.asp?pk_no=1117892'