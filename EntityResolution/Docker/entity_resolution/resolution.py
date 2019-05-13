from sklearn.feature_extraction.text import TfidfVectorizer
import codecs
from utils import *
import argparse
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity as cs


class EntityResolution:
	def __init__(self,input_file,output_path):
		records = []
		self.output_path = output_path
		with open(input_file, "r") as f:
			for record in f:
				records.append(record[:-1])
		self.doc2gpe = {}
		for i in range(len(records)):
			doc_id = json.loads(records[i])["id"]
			if "GPE" not in json.loads(records[i]):
				continue
			for j in json.loads(records[i])["GPE"]:
				if doc_id not in self.doc2gpe:
					self.doc2gpe[doc_id] = set()
				self.doc2gpe[doc_id].add(j)
		self.clean_to_unclean = {}
		self.unclean_to_clean = {}
		self.clean_count = {}
		self.inner_cluster = {}
		self.nodes = []
		self.res = []

	def clean(self):
		for i in self.doc2gpe:
			clean_dict = {}
			clean_dict_un = {}
			clean_count = {}
			for unclean_word in self.doc2gpe[i]:
				clean_word = my_preprocessor(unclean_word)
				clean_dict_un[unclean_word] = clean_word
				if clean_word not in clean_dict:
					clean_dict[clean_word] = []
				clean_dict[clean_word].append(unclean_word)
				if clean_word  not in clean_count:
					clean_count[clean_word] = 0
				clean_count[clean_word] += 1
			self.clean_to_unclean[i] = clean_dict
			self.unclean_to_clean[i] = clean_dict_un
			self.clean_count[i] = clean_count

	def document_cluster(self,entity_dict):
		vector_sample = []
		for j in entity_dict:
			str_ = entity_dict[j]
			if len(str_) > 1:
				vector_sample.append(str_)
		split_list = list(map(generate_ngram, vector_sample))
		abbv_list = list(map(abbv, vector_sample))

		tfidf_vecorizor = TfidfVectorizer(stop_words=[])
		split_list_tf_idf = tfidf_vecorizor.fit_transform(split_list)

		pw = cs(split_list_tf_idf, split_list_tf_idf)
		edge_set = set()
		node_set = set()

		for ii in range(pw.shape[0]):
			node_set.add(ii)
			for j in range(ii, pw.shape[0]):
				if pw[ii][j] > 0.5:
					edge_set.add((ii, j))
				elif pw[ii][j] > 0.3 and abbv_list[ii] == abbv_list[j]:
					edge_set.add((ii, j))
		G = nx.Graph()
		for ii in node_set:
			G.add_node(ii, attribute=vector_sample[ii])
		G.add_edges_from(list(edge_set))
		cp = sorted(nx.connected_components(G), key=len, reverse=True)

		inner_cluster = []
		for j in range(len(cp)):
			clu = []
			for n in cp[j]:
				clu.append(vector_sample[n])
			inner_cluster.append(clu)
		return inner_cluster

	def document_level_cluster(self):
		for i in self.unclean_to_clean:
			self.inner_cluster[i] = self.document_cluster(self.unclean_to_clean[i])

	def global_connected_component(self):
		min_hash_table = {}
		G_all = nx.Graph()
		node_set_all = set()
		edge_set_all = set()
		node_id = 0
		id_to_node = {}
		for doc in self.inner_cluster:
			for clu in  self.inner_cluster[doc]:
				node_set_doc = []
				max_count = 0
				mem = None
				node_id_ = None
				for ent in clu:
					node_set_all.add(node_id)
					node_set_doc.append(node_id)
					id_to_node[node_id]= (ent,doc)
					count = self.clean_count[doc][ent]
					if count > max_count:
						if mem and len(mem)<3:
							continue
						max_count = count
						mem = ent
						node_id_ = node_id
					node_id += 1
				for i in range(len(node_set_doc)-1):
					edge_set_all.add((node_set_doc[i],node_set_doc[i+1]))
				if mem:
					hash_code = getminHash(mem,1)*100 + getminHash(mem,0)
					if hash_code not in min_hash_table:
						min_hash_table[hash_code] = []
					min_hash_table[hash_code].append((mem,doc,node_id_))
		# print(len(min_hash_table))
		for h in min_hash_table:
			hash_node = {}
			for n in min_hash_table[h]:
				word = n[0]
				if word not in hash_node:
					hash_node[word] = []
				hash_node[word].append(n[2])
			check_cluster = list(set(map(lambda x:x[0],min_hash_table[h])))

			split_list = map(generate_ngram, check_cluster)
			tfidf_vecorizor = TfidfVectorizer(stop_words=[])
			split_list_tf_idf = tfidf_vecorizor.fit_transform(split_list)
			pw = cs(split_list_tf_idf, split_list_tf_idf)
			edge_set = set()
			node_set = set()

			for ii in range(pw.shape[0]):
				node_set.add(ii)
				for j in range(ii, pw.shape[0]):
					if pw[ii][j] > 0.5:
						edge_set.add((ii, j))
			G = nx.Graph()
			for ii in node_set:
				G.add_node(ii, attribute=check_cluster[ii])
			G.add_edges_from(list(edge_set))
			cp = sorted(nx.connected_components(G), key=len, reverse=True)
			for j in range(len(cp)):
				clu_node = []
				for n in cp[j]:
					for nn in hash_node[check_cluster[n]]:
						clu_node.append(nn)
				for nod_no in range(len(clu_node)-1):
					edge_set_all.add((clu_node[nod_no], clu_node[nod_no + 1]))

		G_all = nx.Graph()
		G_all.add_edges_from(list(edge_set_all))
		cp = sorted(nx.connected_components(G_all), key=len, reverse=True)
		for clu_node in cp:

			name_count = {}
			mention = []
			for ii in clu_node:
				ent_tuple = id_to_node[ii]
				name = ent_tuple[0]
				doc = ent_tuple[1]
				if name not in name_count:
					name_count[name] = 0
				name_count[name] += self.clean_count[doc][name]
				for ori_mem in self.clean_to_unclean[doc][name]:
					mention.append({"mention":ori_mem,"doc":doc})
			enitiy = {"mention": mention, "name":sorted(name_count.items(),key=lambda x:x[1],reverse=True)[0][0]}
			self.res.append(enitiy)
	def dump(self):
		with codecs.open(self.output_path,"w") as f:
			for json_f in self.res:
				f.write(json.dumps(json_f)+"\n")

	def run(self):
		self.clean()
		self.document_level_cluster()
		self.global_connected_component()
		self.dump()





def args_parse():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", required=True,metavar='input_file', help="path to input file")
	ap.add_argument("-o", required=True, metavar='output_file',help="path to output")
	args = vars(ap.parse_args())
	return args

def main():
	args = args_parse()
	ipath = args["i"]
	opath = args["o"]
	er = EntityResolution(ipath,opath)
	er.run()

if __name__ == '__main__':
  main()

