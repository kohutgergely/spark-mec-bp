MAKEFILE := $(firstword $(MAKEFILE_LIST))
DOCKER_IMAGE_NAME=plasma-characterizer

RUN_IN_DOCKER= \
        docker run --rm \
                -v `pwd`:/app

.PHONY: build
build:
	docker build --tag ${DOCKER_IMAGE_NAME} .

.PHONY: shell
shell: build
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} /bin/bash

.PHONY: run
run: build
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} python entrypoint.py

.PHONY: test
test: build
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} pytest /app

.PHONY: test-ci
test-ci: build
	${RUN_IN_DOCKER} ${DOCKER_IMAGE_NAME} pytest /app

.PHONY: jupyter
jupyter:  build
	${RUN_IN_DOCKER} -p 80:8888 ${DOCKER_IMAGE_NAME} jupyter notebook --port 8888 --allow-root --no-browser --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password=''