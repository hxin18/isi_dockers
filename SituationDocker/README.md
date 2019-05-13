# situation_cluster
This program take the dataset of tweeters and output the situation cluster.

## Format

### tweet json line file
tweet json line file is a json line file, with each line represent a tweet. ofile_nepal is an sample.

Each line should be a json object as follows:
```
{"topic": ["med", "water", "food"], "id": "593673030670229504", "location": "siliguri", "time": "2015-04-30T07:07:35Z", "text": "RT @ArtOfLivingNow: Truckload of toiletries, food packets, water, medicines, & more leaves Siliguri for #NepalQuakeRelief victims. http://t\u2026"}
```

## How to build
Inside docker folder, and run
```
bash build.sh
```
Make sure docker is correctly installed

## How to run

```
usage: docker run -v YOUR_DATA_DIR:/data situationclustering [-c cluster_file] -t original_file -o output_file
                    -thr threshold -gap time gap

arguments:
  -h, --help        show this help message and exit
  -c cluster_file   path to input cluster file
  -t original_file  path to input raw file
  -o output_file    path to output
  -thr threshold    threshold
  -gap time gap     time gap
```

## Sample output
out.json is the sample output by running 

```
docker run -v /Users/xinhuang/Desktop/EntityResolution/Data:/data situationclustering  -t /data/ofile_nepal_all -o /data/out.json -thr 0.6 -gap 1
```
One line is
```
{"cluster151": ["591904342803755008", "591905445989736448", "591920897256083457", "591920994668843008"], "name": "search at kathmandu"}

```