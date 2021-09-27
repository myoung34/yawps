setup:
	poetry install

gen_requirements:
	poetry export -f requirements.txt >requirements.txt

gen_requirements_dev:
	poetry export --dev -f requirements.txt >requirements-dev.txt

.PHONY: build test
build:
	docker run --rm -u root -v $(PWD):/var/task lambci/lambda:build-python3.7 sh -c "python setup.py build; pip install -r requirements.txt -t build/lib"

zip: build
	@cd ./build/lib; \
	  zip -r9 ../../yawps.zip .

test:
	poetry run tox

run:
	docker-compose run lambda
