from fastapi import FastAPI
from app.core.config import settings
from app.api import router_mock, router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Conditional Router Inclusion
if settings.USE_MOCK_PREPROCESSOR:
    print("INFO:     Loading MOCK Data Preprocessor Endpoints")
    app.include_router(router_mock.router, prefix=f"{settings.API_V1_STR}/preprocessor", tags=["Mock Preprocessor"])
else:
    print("INFO:     Loading Data Preprocessor Endpoints")
    app.include_router(router.router, prefix=f"{settings.API_V1_STR}/preprocessor", tags=["Real Preprocessor"])

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "using_mock": settings.USE_MOCK_PREPROCESSOR
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "using_mock": settings.USE_MOCK_PREPROCESSOR}
