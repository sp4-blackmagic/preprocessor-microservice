# Setup

### Initialize virtual environment
```bash
uv venv
source .venv/bin/activate
```

### Install all dependencies 
```bash
uv sync
```

### Install just
```bash
<PACKAGE_MANAGER> install just
```
If having problems, refer to https://github.com/casey/just

# Usage

### Run the service
```bash
uv uvicorn app.main:app --reload --port 8001
```
or
```bash
just run
```

### Fetching data
Explain here

*`app.main:app` means: in the `app/main.py` file, find the FastAPI instance named `app`.*

# Docker
To run the service as a docker container follow the steps below

### Build and run the container
```bash
docker build -t preprocessor-service .   
docker run -p 8001:8001 preprocessor-service
```
or
```bash
just run-docker
```

# Misc
### Running tests
```bash
just test
```
### Linting
```bash
just lint
```