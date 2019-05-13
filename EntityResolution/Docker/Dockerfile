FROM python:3-onbuild  

# Coping source in current directory into the image
# python:3-onbuild expects the source in /usr/src/app
COPY . /usr/src/app
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
WORKDIR /usr/src/app/entity_resolution

# Commands in a list
ENTRYPOINT ["python", "resolution.py"]