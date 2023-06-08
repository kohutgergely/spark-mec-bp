FROM python:3.9

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:/app

ENTRYPOINT ["python", "app.py"]