import string
import random
from nltk.corpus import stopwords
import json
def my_preprocessor(text):
	text = text.replace("\n","")
	text = text.replace("\\n","")
	text = text.replace("&quot","")
	pos = text.find("http")
	if pos!=-1:
		text = text[:pos]
	# Remove punctuation and lowercase
	punctuation=set(string.punctuation)

	words=text.split(" ")
	words2=[]

	for x in words:
		if x[0:5]!="http:":
			words2.append(x)
	doc=' '.join(words2)
	numbers = ["1","2","3","4","5","6","7","8","9","0"]
	temp=[]
	for letter in doc:
		if not letter in punctuation and letter not in numbers and ord(letter)<128:
			temp.append(letter)
		else:
			temp.append('')
	text=''.join(temp)
	text = ' '.join([x for x in text.split() if x not in set(stopwords.words('english'))])
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


def getminHash(word, seed):
	random.seed(seed)
	word_dict = {}
	for i in range(26):
		word_dict[i] = chr(i + ord('a'))
	all_list = list(range(26))
	hash_code = 0
	while len(all_list) > 0:
		idx = random.randint(0, len(all_list) - 1)
		if word_dict[all_list[idx]] in word:
			return hash_code
		all_list[idx] = all_list[len(all_list) - 1]
		all_list = all_list[:len(all_list) - 1]
		hash_code += 1
	return len(word_dict)

def get_blocking(path_to_cluster_heads, seed1, seed2, transDict, bn_prefix):

	blocks = {}

	cluster_heads = json.load(open(path_to_cluster_heads))
	IDs = list(cluster_heads.keys())
	print(len(IDs))
	count = 0
	for id1 in IDs:
		count += 1
		if count % 10000 == 0:
			print(count * 1.0 / len(IDs))
		word = cluster_heads[id1][0]
		block_name = bn_prefix + str(getminHash(word, seed1) * 100 + getminHash(word, seed2) * 1)
		if block_name not in blocks:
			blocks[block_name] = []
		blocks[block_name].append(id1)
	return blocks


def abbv(word):
	list_res = []
	punctuation=set(string.punctuation)
	temp=[]
	for letter in word:
		if not letter in punctuation:
			temp.append(letter)
	word=''.join(temp)
	word_list = word.split()
	to_append = []
	if(len(word_list)==1):
		to_append.append(word_list[0])
	if(len(word_list)>1):
		words = ""
		for i in word_list:
			words+=i[0]
		to_append.append(words)
	return str(" ".join(to_append))