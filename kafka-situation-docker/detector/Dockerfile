FROM python:3-onbuild  

COPY . /usr/src/app
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
WORKDIR /usr/src/app

ENTRYPOINT ["python3", "app.py"]

