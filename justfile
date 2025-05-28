# activate uv
start-uv:
  source .venv/bin/activate

# linting
lint:
  flake8 ./app ./tests

# testing
test: 
  pytest

# run the service
run:
  uvicorn app.main:app --reload --port 8001

# build a docker container
build-docker:
  docker build -t preprocessor-service .

# run the microservice docker container
run-docker: build-docker
  docker run -p 8001:8001 preprocessor-service

# run the microservice docker container in the background
run-docker-detached: build-docker
  docker run -d -p 8001:8001 preprocessor-service

# docker run --name preprocessor-service -d -p 8001:8001 preprocessor-service