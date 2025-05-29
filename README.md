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
Once the service is started, preprocessing can be requested by making a **multipart/form-data** call to the endpoint :
```bash
# If running locally
http://127.0.0.1:8001/preprocessor/api/preprocess
# If running with docker
http://0.0.0.0:8001/preprocessor/api/preprocess
```
This request will expect specific key-value pairs in the form:
- `hdr_file` of type File, which accepts the header file of the hyperspectral image you wish to process
- `cube_file` of type File, which accepts either a `.bin` or `.raw` extension file which contains the data to the corresponding header file
- **optional**: params of type Text, where each parameter from `app/schemas/data_models.py/PreprocessingParameters` can be specified individually, so and example of such a pair would be `remove_background (type Text) - False`. \
The parameters that are not specified in the request will assume default values

The response will be raw text formatted like a `.csv` file.


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