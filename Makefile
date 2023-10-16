HOST = 0.0.0.0
PORT = 8800

install:
	poetry install

tests: install
	poetry run flake8 . --count --show-source --statistics --max-line-length=88 --extend-ignore=E203
	poetry run black . --check
	poetry run isort . --profile=black
	poetry run pytest --cov=./ --cov-report=xml

export:
	poetry export -f requirements.txt -o requirements.txt --without-hashes

update_index:
	cp README.md docs/index.md

run: install
	poetry run uvicorn truck_counting.main:app --reload --host ${HOST} --port ${PORT}

build:
	docker build -t truck-counting:latest .

deploy:
	docker run -d -p 8000:80 --name truck-counting-container --env-file .env truck-counting:latest

rmcontainer:
	docker container rm truck-counting-container --force

rmimage:
	docker image rm truck-counting:latest

build_deploy: build deploy

rmall: rmcontainer rmimage

redeploy: rmall build_deploy

logs:
	docker logs truck-counting-container
