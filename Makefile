.PHONY: build run stop logs

CONTAINER_NAME = tc-loft-takehome
TAG = latest

build:
	docker build -t $(CONTAINER_NAME):$(TAG) .

run:
	docker run -d --name $(CONTAINER_NAME) $(CONTAINER_NAME):$(TAG)

stop:
	docker stop $(CONTAINER_NAME)

logs:
	docker logs -f $(CONTAINER_NAME)