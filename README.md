# Setup

### Initialize virtual environment
```bash
uv venv
source .venv/bin/activate
```

### Install all dependencies 
```bash
uv pip install .
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

### Fetching data
For now this is a mock solution, so it returns an example csv with some hyperspectral data.
While the service is running, make a POST request to the endpoint:
```http://127.0.0.1:8001/preprocessor/api/preprocess```

*`app.main:app` means: in the `app/main.py` file, find the FastAPI instance named `app`.*

# Docker
To run the service as a docker container follow the steps below

### Build and run the container
```bash
docker build -t preprocessor-service .   
docker run -p 8001:8001 preprocessor-service
```