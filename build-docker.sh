#!/bin/bash

set -e

if [[ "$OSTYPE" == "linux"* ]]; then
	DOCKER_BUILDKIT=1 docker build . -f Dockerfile.buildkit -t vamos:fase
else
	docker build . -t vamos:fase
fi

echo "Run command:"
echo "docker run -ti -v "$(pwd)/results":/opt/results  vamos:fase"
