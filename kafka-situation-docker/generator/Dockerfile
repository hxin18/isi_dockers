FROM python:3-onbuild  

COPY . /usr/src/app
RUN cat requirements.txt
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
WORKDIR /usr/src/app

CMD ["python3", "app.py"]
