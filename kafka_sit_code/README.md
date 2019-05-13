# situation_cluster
This program take the dataset of tweeters and output the situation cluster.

## Format

### tweet json line file
tweet json line file is a json line file, with each line represent a tweet. ofile_nepal is an sample.

Each line should be a json object as follows:
```
{"topic": ["med", "water", "food"], "id": "593673030670229504", "location": "siliguri", "time": "2015-04-30T07:07:35Z", "text": "RT @ArtOfLivingNow: Truckload of toiletries, food packets, water, medicines, & more leaves Siliguri for #NepalQuakeRelief victims. http://t\u2026"}
```

## pre-requisite

Please make sure kafka server are correctly configurated and run. Please modified the Consumer_back.py and Producer_front.py for the correct host

use python 3 and install all requirements

```
pip -r requirements.txt
```

## How to run

Server:
```
python Consumer_back.py [-h] -o output_file -thr threshold -gap time gap

optional arguments:
  -h, --help      show this help message and exit
  -o output_file  path to output
  -thr threshold  threshold
  -gap time gap   time gap
```

## Sample output
out.json is the sample output by running 
```
python Producer_front.py
```
One line is
```
{"cluster151": ["591904342803755008", "591905445989736448", "591920897256083457", "591920994668843008"], "name": "search at kathmandu"}

```


## Progamming

Init or refresh the server
```python
msg_dict ={"method":"init"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg, partition=0)
```
sending message
```python
msg_dict ={"method":"update","data":data}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)
```
Data should be:
```
 {"id": tid, "text": ttext, "time": ttime, "location": tlocation,"type": ttype}
```

dump file 
```python
msg_dict ={"method":"dump"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)
```

shut down server

```python
msg_dict ={"method":"exit"}
msg = json.dumps(msg_dict)
producer.send('test_rhj', msg)
```
