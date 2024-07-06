FROM python:3.10.6-buster

WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip

COPY POC.py POC.py
COPY pages/ pages/
COPY Makefile Makefile

RUN make all

EXPOSE 8501
CMD streamlit run POC.py
