FROM python:3.10.6-buster

WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip

COPY app.py app.py
COPY Makefile Makefile

RUN make all

EXPOSE 8501
CMD streamlit run app.py
