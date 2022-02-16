DOCKER_IMAGE_NAME=`basename ${PWD}`

RUN_IN_DOCKER= \
        docker run --rm \
                -v `pwd`:/app

.PHONY: build
build:
	docker build --tag ${DOCKER_IMAGE_NAME} .

.PHONY: shell
shell:
	${RUN_IN_DOCKER} --entrypoint '' -it ${DOCKER_IMAGE_NAME} /bin/bash

.PHONY: run
run: 
	${RUN_IN_DOCKER} --entrypoint '' -it ${DOCKER_IMAGE_NAME} python app.py