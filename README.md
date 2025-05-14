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

# Usage

### Run the service
```bash
uv uvicorn app.main:app --reload --port 8001
```

### Fetching data
For now this is a mock solution, so it returns an example csv with some hyperspectral data.
While the service is running, make a POST request to the endpoint:
`http://127.0.0.1:8001/api/v1/preprocessor/preprocess`