"""Example Kafka consumer."""

import json
import os

from kafka import KafkaConsumer

import codecs
import json
from datetime import  datetime
from situation.clusters import *
from situation.utils import *
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import metrics
import argparse
import string

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')
LEGIT_TOPIC = os.environ.get('LEGIT_TOPIC')
FRAUD_TOPIC = os.environ.get('FRAUD_TOPIC')



class StreamingCluster:
    def __init__(self,threshold,time_gap,opath):
        self.output_path = opath
        self.threshold = float(threshold)
        self.time_gap = float(time_gap)
        self.tweet_dataset = {}
        self.data = []
        self.frozen_cluster = []
        self.clusters = []
        self.global_loc = {}
        self.id_to_ngram = {}
        self.cluster_id = 0
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
        self.vectorize = vectorizer.fit(list(set_all))


    def run(self):
        consumer = KafkaConsumer('test_rhj', bootstrap_servers=KAFKA_BROKER_URL)
        i = 1
        for msg in consumer:
            msg_val = json.loads(msg.value.decode("utf-8"))
            msg_val = json.loads(msg_val)
            method = msg_val["method"]
            # print(i)
            # i+=1
            if method == "init":
                self.frozen_cluster = []
                self.clusters = []
                self.global_loc = {}
                self.id_to_ngram = {}
                self.cluster_id = 0
            elif method == "exit":
                return
            elif method == "update":
                tweet = msg_val["data"]
                c_text = tweet["text"]
                self.id_to_ngram[tweet["id"]] = self.vectorize.transform([generate_ngram(c_text)]).astype('float64')
                print("msg "+str(len(self.id_to_ngram))+ " comes")
                id_to_ngram = self.id_to_ngram
                if len(self.clusters) == 0:
                    self.cluster_id += 1
                    clu = Cluster(self.cluster_id);
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
                            self.cluster_id += 1
                            clu = Cluster(self.cluster_id);
                            clu.last_update = tweet["time"]
                            clu.docs = [tweet["id"]]
                            clu.center = id_to_ngram[tweet["id"]]
                            self.clusters.append(clu)
                    else:
                        if not all_satisfied:
                            self.cluster_id += 1
                            clu = Cluster(self.cluster_id);
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
            elif method == "dump":
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
    # ap.add_argument("-c", required=True,metavar='cluster_file', help="path to input cluster file")
    # ap.add_argument("-t", required=True,metavar='original_file', help="path to input raw file")
    ap.add_argument("-o", required=True, metavar='output_file',help="path to output")
    ap.add_argument("-thr", required=True, metavar='threshold', help="threshold")
    ap.add_argument("-gap", required=True, metavar='time gap', help="time gap")
    args = vars(ap.parse_args())
    return args

def main():
    args = args_parse()
    # cpath = args["c"]
    # tpath = args["t"]
    opath = args["o"]
    thr =  args["thr"]
    gap =  args["gap"]
    # sc = StreamingCluster(tpath,cpath,opath,thr,gap)
    sc = StreamingCluster(thr,gap,opath)
    sc.run()
    # sc.eva()

if __name__ == '__main__':
  main()




