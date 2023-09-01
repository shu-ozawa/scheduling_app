FROM python:3.7.12-slim-buster

WORKDIR /scheduling_app

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y upgrade && \
    pip install -r requirements.txt

EXPOSE 8500

COPY . /scheduling_app

ENTRYPOINT ["streamlit", "run"]

CMD ["main.py"]
