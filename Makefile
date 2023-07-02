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
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} python app.py

.PHONY: test
test: build
	${RUN_IN_DOCKER} -it ${DOCKER_IMAGE_NAME} pytest /app

.PHONY: test-ci
test-ci: build
	${RUN_IN_DOCKER} ${DOCKER_IMAGE_NAME} pytest /app
