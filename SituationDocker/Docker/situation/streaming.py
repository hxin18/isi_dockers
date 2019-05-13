import codecs
import json
from utils import *
from datetime import  datetime
from clusters import *
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import metrics
import argparse

class StreamingCluster:
	def __init__(self,ofile,cfile,output_path,threshold,time_gap):
		self.cfile = cfile
		self.threshold = float(threshold)
		self.time_gap = float(time_gap)
		self.tweet_dataset = {}
		self.data = []
		self.curr_run_data = []
		self.ground_truth = {}
		self.frozen_cluster = []
		self.clusters = []
		self.global_loc = {}
		self.output_path = output_path
		with codecs.open(ofile, "r", "utf-8-sig") as f:
			for line in f:
				d = json.loads(line)
				tid = d[u'id']
				ttext = d["text"]
				ttime = d["time"]
				if "topic" in d:
					ttype = d["topic"]
				else:
					ttype = None
				if "location" in d:
					tlocation = d["location"]
				else:
					tlocation = None
				if len(my_preprocessor(ttext)) < 1:
					continue
				self.tweet_dataset[tid] = {"id": tid, "text": ttext, "time": ttime, "location": tlocation, "type": ttype}
				self.data.append(self.tweet_dataset[tid])
		if cfile:
			with codecs.open(cfile, "r", "utf-8-sig") as f:
				idx_ = 0
				for line in f:
					idx_ += 1
					cluster = json.loads(line)
					cid = idx_
					doc = cluster["doc"]
					self.ground_truth[cid] = doc


	def eva(self):
		if not self.cfile:
			return
		# print(len(self.curr_run_data))
		ground_truth = []
		ground_id = []
		pos_to_id = {}
		idx_ = 0
		for line in self.ground_truth:
			idx_ += 1
			cluster = self.ground_truth[line]
			temp = []
			for d in cluster:
				if d in self.curr_run_data:
					temp.append(d)
			if(len(temp)<2):
				continue
			cid = idx_
			for d in temp:
				ground_truth.append(cid)
				pos_to_id[d] = len(ground_id)
				ground_id.append(d)

		curr_ = [0 for d in pos_to_id]
		# idx_ = 0
		if not curr_:
			return
		for c in self.frozen_cluster:
			if len(c.docs) > 0:
				idx_ = max(curr_)+1
				for d in c.docs:
					if d in pos_to_id:
						curr_[pos_to_id[d]] = idx_
		for c in self.clusters:
			if len(c.docs) > 0:
				idx_ = max(curr_)+1
				for d in c.docs:
					if d in pos_to_id:
						curr_[pos_to_id[d]] = idx_

		print("%.6f" % metrics.homogeneity_score(ground_truth, curr_))
		print("%.6f" % metrics.completeness_score(ground_truth, curr_))
		print("%.6f" % metrics.v_measure_score(ground_truth, curr_))
		print("%.6f" % metrics.adjusted_mutual_info_score(ground_truth, curr_))
		print("%.6f" % metrics.adjusted_rand_score(ground_truth, curr_))


	def run(self):
		data_stream = sorted(self.data, key=lambda x: datetime.strptime(x["time"], '%Y-%m-%dT%H:%M:%SZ'))
		# data_stream = sorted(self.data, key=lambda x: datetime.strptime(x["time"], "%a %b %d  %H:%M:%S GMT %Y"))
		cluster_id = 0
		vectorizer = CountVectorizer()
		set_all = set()
		all_ = list(string.ascii_lowercase)
		all_.append("_")
		temp = ""
		for i in all_:
			temp += i
			for j in all_:
				temp += j
				for k in all_:
					temp += k
					set_all.add(temp)
					temp = temp[:len(temp) - 1]
				temp = temp[:len(temp) - 1]
			temp = temp[:len(temp) - 1]
		all_clean_word = []
		for t in data_stream:
			c_text = my_preprocessor(t["text"])
			if len(c_text) > 0:
				all_clean_word.append(generate_ngram(c_text))

		vectorize = vectorizer.fit(list(set_all))
		self.id_to_ngram = {}

		for t in data_stream:
			c_text = my_preprocessor(t["text"])
			self.id_to_ngram[t["id"]] = vectorize.transform([generate_ngram(c_text)]).astype('float64')

		id_to_ngram = self.id_to_ngram
		for tweet in data_stream:
			# case for add new cluster
			if (len(self.curr_run_data) % 200 == 1):
				print("reading "+str(len(self.curr_run_data))+" document")
			self.curr_run_data.append(tweet['id'])
			if len(self.clusters) == 0:
				cluster_id += 1
				clu = Cluster(cluster_id);
				clu.last_update = tweet["time"]
				clu.docs = [tweet["id"]]
				clu.center = id_to_ngram[tweet["id"]]
				if tweet["type"]:
					clu.update_type(tweet["type"])
				if tweet["location"]:
					if tweet["location"] not in self.global_loc:
						self.global_loc[tweet["location"]] = 0
					self.global_loc[tweet["location"]] += 1
					clu.update_loc(tweet["location"],self.global_loc)
				self.clusters.append(clu)
			else:
				maxx = 0
				curr = 0
				all_satisfied = []
				for idx, c in enumerate(self.clusters):
					cosine_sim = cosine_similarity(id_to_ngram[tweet["id"]], c.center)
					if cosine_sim[0][0] > curr:
						curr = cosine_sim[0][0]
						maxx = idx
					if cosine_sim[0][0]>self.threshold:
						all_satisfied.append((idx,cosine_sim[0][0]))
				if not tweet["location"]:
					if curr > self.threshold:
						c_updated = self.clusters[maxx]
						c_updated.center = len(c_updated.docs) * c_updated.center + id_to_ngram[tweet["id"]]
						c_updated.docs.append(tweet["id"])
						c_updated.last_update = tweet["time"]
						c_updated.center /= len(c_updated.docs)
					else:
						cluster_id += 1
						clu = Cluster(cluster_id);
						clu.last_update = tweet["time"]
						clu.docs = [tweet["id"]]
						clu.center = id_to_ngram[tweet["id"]]
						self.clusters.append(clu)
				else:
					if not all_satisfied:
						cluster_id += 1
						clu = Cluster(cluster_id);
						clu.last_update = tweet["time"]
						clu.docs = [tweet["id"]]
						clu.center = id_to_ngram[tweet["id"]]
						if tweet["type"]:
							clu.update_type(tweet["type"])
						if tweet["location"]:
							if tweet["location"] not in self.global_loc:
								self.global_loc[tweet["location"]] = 0
							self.global_loc[tweet["location"]] += 1
							clu.update_loc(tweet["location"], self.global_loc)
						self.clusters.append(clu)
					else:
						loc_t = tweet["location"]
						flg = False
						new_all = []
						for idx_c, c in  enumerate(all_satisfied):
							if self.clusters[c[0]].showed_loc == loc_t:
								flg = True
								new_all.append((all_satisfied[idx_c][0], all_satisfied[idx_c][1] + 1))
							else:
								new_all.append(all_satisfied[idx_c])
						if not flg:
							c_updated = self.clusters[maxx]
							c_updated.center = len(c_updated.docs) * c_updated.center + id_to_ngram[tweet["id"]]
							c_updated.docs.append(tweet["id"])
							c_updated.last_update = tweet["time"]
							c_updated.center /= len(c_updated.docs)
						else:
							c_updated = self.clusters[sorted(new_all,key=lambda x:x[1],reverse=True)[0][0]]
							c_updated.center = len(c_updated.docs) * c_updated.center + id_to_ngram[tweet["id"]]
							c_updated.docs.append(tweet["id"])
							c_updated.last_update = tweet["time"]
							c_updated.center /= len(c_updated.docs)
							if tweet["type"]:
								clu.update_type(tweet["type"])
							if tweet["location"]:
								if tweet["location"] not in self.global_loc:
									self.global_loc[tweet["location"]] = 0
								self.global_loc[tweet["location"]] += 1
								c_updated.update_loc(tweet["location"], self.global_loc)
				time_cur = datetime.strptime(tweet["time"], '%Y-%m-%dT%H:%M:%SZ')
				# time_cur = datetime.strptime(tweet["time"], "%a %b %d  %H:%M:%S GMT %Y")
				del_set = []
				for cl_idx , cl in enumerate(self.clusters):
					str_ = cl.last_update
					# duration = (time_cur - datetime.strptime(str_, "%a %b %d  %H:%M:%S GMT %Y"))
					duration = (time_cur - datetime.strptime(str_, '%Y-%m-%dT%H:%M:%SZ'))
					if duration.days >= self.time_gap:
						del_set.append(cl_idx)
				del_ = 0
				for c in del_set:
					self.frozen_cluster.append(self.clusters[c-del_])
					self.clusters = self.clusters[:c-del_] + self.clusters[c-del_ + 1:]
					del_+= 1
		idx_ = 1
		with codecs.open(self.output_path, "w") as f:
			for c in self.frozen_cluster:
				if len(c.docs) > 0:
					topic = c.showed_type
					location = c.showed_loc
					name = None
					if topic:
						name = topic
						if location:
							name += " at "+ location
						else:
							name += " at some where"
					f.write(json.dumps({"cluster" + str(idx_): c.docs, "name":name}) + "\n")
					idx_ += 1
			for rc in self.clusters:
				if len(rc.docs) > 0:
					topic = rc.showed_type
					location = rc.showed_loc
					name = None
					if topic:
						name = topic
						if location:
							name += " at " + location
						else:
							name += " at some where"
					f.write(json.dumps({"cluster" + str(idx_): rc.docs, "name":name}) + "\n")
					idx_ += 1







def args_parse():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", metavar='cluster_file', help="path to input cluster file")
	ap.add_argument("-t", required=True,metavar='original_file', help="path to input raw file")
	ap.add_argument("-o", required=True, metavar='output_file',help="path to output")
	ap.add_argument("-thr", required=True, metavar='threshold', help="threshold")
	ap.add_argument("-gap", required=True, metavar='time gap', help="time gap")
	args = vars(ap.parse_args())
	return args

def main():
	args = args_parse()
	if "c" in args:
		cpath = args["c"]
	else:
		cpath = None
	tpath = args["t"]
	opath = args["o"]
	thr =  args["thr"]
	gap = args["gap"]
	sc = StreamingCluster(tpath,cpath,opath,thr,gap)
	sc.run()
	sc.eva()
	print("finished")

if __name__ == '__main__':
  main()
