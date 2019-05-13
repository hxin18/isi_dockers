import re
import string
from nltk.corpus import stopwords

def my_preprocessor(text):
	'''
	:param text:
	:return:
	'''
	text = text.replace("\n"," ")
	# Remove punctuation and lowercase
	punctuation=set(string.punctuation)
	pattern_html =r"http\S+"
	html_line = re.findall(pattern_html,text)
	text = " ".join([x for x in text.split(" ") if x not in html_line])
	pattern =r"[a-zA-Z]+"
	words = re.findall(pattern,text)
	doc=' '.join(words)
	temp=[]
	number = list(map(str,range(10)))
	for letter in doc:
		if not letter in punctuation and letter not in number:
			temp.append(letter)
		else:
			temp.append(' ')
	text=''.join(filter(lambda x: ord(x)<128,temp))
	text = ' '.join([x for x in text.split() if x.lower() not in set(stopwords.words('english')) and len(x)>3])
	return text.lower()


def ngram_word(word):
	list_res = []
	word_ = "__" + word + "__"
	for i in range(0, len(word_) - 2):
		list_res.append(word_[i:i + 3])
	return list_res
def generate_ngram(word):
	list_res = []
	punctuation = set(string.punctuation)
	temp = []
	for letter in word:
		if not letter in punctuation:
			temp.append(letter)
	word = ''.join(temp)
	word_list = word.split()
	for words in word_list:
		l = ngram_word(words)
		for ii in l:
			list_res.append(''.join(filter(lambda x: ord(x) < 128, ii)))
	return str(" ".join(list_res))