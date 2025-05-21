from fastapi import FastAPI
from app.core.config import settings, PreprocessorVersion
from app.api import router, router_stub

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# Conditional Router Inclusion
if settings.PREPROCESSOR_VERSION == PreprocessorVersion.STUB:
    print("INFO: Loading Stub Data Preprocessor Endpoints")
    app.include_router(router_stub.router, prefix=settings.API_STR, tags=["Stub Preprocessor"])
elif settings.PREPROCESSOR_VERSION == PreprocessorVersion.MOCK:
    print("INFO: Loading Mock Data Preprocessor Endpoints")
    # app.include_router(router_mock.router, prefix=settings.API_STR, tags=["Mock Preprocessor"])
else:
    print("INFO: Loading Data Preprocessor Endpoints")
    app.include_router(router.router, prefix=settings.API_STR, tags=["Production Preprocessor"])

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.PREPROCESSOR_VERSION.name
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok", 
        "version": settings.PREPROCESSOR_VERSION.name
    }
