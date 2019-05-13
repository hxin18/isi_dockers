# Entity resolution
This program take the dataset json line file and out put the entity resolution for the GPE of the tweet.

## Format

### dataset json line file
dataset json line file is a json line file, with each line represent a cluster. cfile.json is an sample.

Each line should be a json object as follows:
```
{"LOC": ["Gorkha District"], "originalText": "RT @abcnews: Nepal earthquake: No food, no clothes, no shelter, say locals from Gorkha District at epicentre of quake http://t.co/D50mx9u4p\u2026", "language": "en", "geoLocations": [{"lat": 28, "geohash": "tugxr3nzvf79", "lon": 84}, {"lat": 31.41423, "geohash": "ttt68nu91ucv", "lon": 74.88906999999999}], "translatedText": "RT @abcnews: Nepal earthquake: No food, no clothes, no shelter, say locals from Gorkha District at epicentre of quake http://t.co/D50mx9u4p\u2026", "topics": ["shelter", "food"], "hashTags": [], "sentimentString": "Activation", "GPE": ["Nepal"], "ORG": ["RT"], "id": 593647103424925700, "createdAt": "2015-04-30T01:24:33Z", "screenName": "brownsauce2010"}
```
id field are required and we mainly use GPE field.

## How to build
Inside docker folder, and run
```
bash build.sh
```
Make sure docker is correctly installed

## How to run

```
usage: docker run -v YOUR_DATA_DIR:/data entityresolution -i input_file -o output_file

arguments:
  -h, --help        show this help message and exit
  -i cluster_file   path to input file
  -o output_file    path to output
```

## Sample output
out.json is the sample output by running 

```
docker run -v /Users/xinhuang/Desktop/EntityResolution/Data:/data entityresolution  -i /data/data_sample.jl -o /data/out.json
```
One line is
```
{"mention": [{"mention": "Bhaktapur", "doc": 591906660869754900}, {"mention": "Bhaktapur", "doc": 591935857218691100}], "name": "bhaktapur"}

```
This means that "Bhaktapur" from doc 591906660869754900 and "Bhaktapur" from doc 591935857218691100 are same entity whose name is "bhaktapur".
