#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import codecs,os
from  situation.utils import *
from kafka import KafkaProducer

TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_PER_SECOND = float(os.environ.get('TRANSACTIONS_PER_SECOND'))
SLEEP_TIME = 1 / TRANSACTIONS_PER_SECOND


producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'),bootstrap_servers=KAFKA_BROKER_URL)

tweet_dataset = {}
data = []
with codecs.open("/data/ofile_nepal_all", "r", "utf-8-sig") as f:
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


msg_dict ={"method":"init"}#init the server or refresh it
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg, partition=0)

#sending dara
for i in range(len(data)):
    if (i+1)%100 == 0:
        print(i)
    msg_dict ={"method":"update","data":data[i]}
    msg = json.dumps(msg_dict)
    producer.send('test_rhj', msg)

#dump
msg_dict ={"method":"dump"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)

#shutdown
msg_dict ={"method":"exit"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)
producer.close()




