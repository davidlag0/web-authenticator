.PHONY: clean build run stop inspect

IMAGE_NAME = web-auth
CONTAINER_NAME = web-auth

build:
	podman build -t $(IMAGE_NAME) .

#release:
#	docker build \
#		--build-arg VCS_REF=`git rev-parse --short HEAD` \
#		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` -t $(IMAGE_NAME) .

run:
	podman run --rm --expose 5000 --name $(CONTAINER_NAME) \
	--pod pod -v $(PWD)/app:/app:Z,ro $(IMAGE_NAME)

inspect:
	podman inspect $(CONTAINER_NAME)

shell:
	podman exec -it $(CONTAINER_NAME) /bin/ash

stop:
	podman stop $(CONTAINER_NAME)

#clean:
#	docker ps -a | grep '$(CONTAINER_NAME)' | awk '{print $$1}' | xargs docker rm \
#	docker images | grep '$(IMAGE_NAME)' | awk '{print $$3}' | xargs docker rmi
