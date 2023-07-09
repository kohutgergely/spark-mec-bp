MAKEFILE := $(firstword $(MAKEFILE_LIST))
DOCKER_IMAGE_NAME=spark-mec-bp
DOCKER_TEST_IMAGE_NAME=spark-mec-bp-test

RUN_IN_DOCKER= \
        docker run --rm \
                -v `pwd`:/app

.PHONY: build
build:
	docker build --tag ${DOCKER_IMAGE_NAME} .

.PHONY: build-test
build-test: build
	docker build -f Dockerfile.test --build-arg prod_docker_image=${DOCKER_IMAGE_NAME} --tag ${DOCKER_TEST_IMAGE_NAME} .

.PHONY: run
run: build
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} python entrypoint.py

.PHONY: shell
shell: build-test
	${RUN_IN_DOCKER} -it ${DOCKER_TEST_IMAGE_NAME} /bin/bash

.PHONY: test
test: build-test
	${RUN_IN_DOCKER} -it ${DOCKER_TEST_IMAGE_NAME} pytest

.PHONY: lint
lint: build-test
	${RUN_IN_DOCKER} ${DOCKER_TEST_IMAGE_NAME} flake8

.PHONY: test-ci
test-ci: build-test
	${RUN_IN_DOCKER} ${DOCKER_TEST_IMAGE_NAME} pytest

.PHONY: jupyter
jupyter:  build-test
	${RUN_IN_DOCKER} -p 80:8888 ${DOCKER_TEST_IMAGE_NAME} jupyter notebook --port 8888 --allow-root --no-browser --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password=''