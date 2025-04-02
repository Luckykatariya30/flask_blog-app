FROM python:slim

WORKDIR /app

COPY . .


RUN pip install -r requirements.txt


ENTRYPOINT [ "python", "run.py" ]