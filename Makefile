install:
	@pipenv install
	@mkdir data

devdatabase:
	@pipenv run python dev_data.py

devenvironment: install devdatabase
	@pipenv install --dev

test:
	@pipenv run pytest

server:
	@pipenv run python app.py

clean:
	@pipenv --rm
	@rm -rf data