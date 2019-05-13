#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import codecs
from  situation.utils import *
from kafka import KafkaProducer


producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'),bootstrap_servers='localhost:9092')

tweet_dataset = {}
data = []
with codecs.open("/Users/xinhuang/Documents/isi/situation/ofile_nepal_all", "r", "utf-8-sig") as f:
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
		tweet_dataset[tid] = {"id": tid, "text": my_preprocessor(ttext), "time": ttime, "location": tlocation,"type": ttype}
		data.append(tweet_dataset[tid])

msg_dict ={"method":"init"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg, partition=0)

for i in range(len(data)):
	if (i+1)%100 == 0:
		print(i)
	msg_dict ={"method":"update","data":data[i]}
	msg = json.dumps(msg_dict)
	producer.send('test_rhj', msg)

msg_dict ={"method":"dump"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)


msg_dict ={"method":"exit"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)
producer.close()




