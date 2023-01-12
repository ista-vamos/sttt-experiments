#!/bin/bash

if [[ "$OSTYPE" == "linux"* ]]; then
	DOCKER_BUILDKIT=1 docker build . -f Dockerfile.buildkit
else
	docker build .
fi
