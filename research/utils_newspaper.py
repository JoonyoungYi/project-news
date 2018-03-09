from newspaper import Article

def get_title_text(url):
	article = Article(url, language='ko')
	article.download()
	article.parse()
	title = article.title
	text = article.text
	return title, text