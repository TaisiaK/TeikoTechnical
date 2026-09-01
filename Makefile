.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis

dashboard:
	python -m streamlit run dashboard.py
