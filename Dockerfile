FROM python:3.7.2-alpine

COPY ./* /work/
WORKDIR /work


RUN pip install -r requirements.txt

EXPOSE 10111
CMD python app.py
