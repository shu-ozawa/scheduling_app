FROM python:3.9.17-slim-buster

WORKDIR /scheduling_app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN apt-get update 
RUN apt-get -y upgrade
RUN pip install -r requirements.txt

EXPOSE 8500

COPY . /scheduling_app

ENTRYPOINT ["streamlit", "run"]

CMD ["main.py"]
