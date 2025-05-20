from app.core.config import settings

def test_service_alive(client):
    """
    Test if the service was properly started
    """
    response = client.get("/")
    assert response.status_code == 200

def test_preprocess_mock(client):
    """
    If running in the mock environment, check if the 
    mock preprocessor correctly returns data when being called
    its specific POST request
    """
    if settings.USE_MOCK_PREPROCESSOR:
        response = client.post("/preprocessor/api/preprocess") 
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
    else:
        # Test for real preprocessor here
        assert True