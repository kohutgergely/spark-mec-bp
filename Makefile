DOCKER_IMAGE_NAME=plasma-characterizer

RUN_IN_DOCKER= \
        docker run --rm \
                -v `pwd`:/app

.PHONY: build
build:
	docker build --tag ${DOCKER_IMAGE_NAME} .

.PHONY: shell
shell: build
	${RUN_IN_DOCKER} -p 8888:8888 --entrypoint '' -it ${DOCKER_IMAGE_NAME} /bin/bash

.PHONY: run
run: build
	${RUN_IN_DOCKER} --entrypoint '' -it ${DOCKER_IMAGE_NAME} python app.py

.PHONY: jupyter
jupyter: 
	${RUN_IN_DOCKER} -p 8888:8888 ${DOCKER_IMAGE_NAME} jupyter notebook --port 8888 --allow-root --no-browser --ip=0.0.0.0