install:
	@pip install -r requirements.txt

streamlit:
	-@streamlit run app.py

clean:
	@rm -fr */__pycache__
	@rm -fr __init__.py
	@rm -fr build
	@rm -fr dist
	@rm -fr *.dist-info
	@rm -fr *.egg-info
	-@rm model.joblib

all: install clean
