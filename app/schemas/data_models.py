from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class PreprocessingInput(BaseModel):
    # Example: Define what data your preprocessor will eventually take
    # This could be a list of records, a file ID, raw text, etc.
    data_source_identifier: str # e.g., a URI to S3, a database query, etc.
    parameters: Optional[Dict[str, Any]] = None

# For CSV output, FastAPI handles StreamingResponse/FileResponse well,
# so a specific Pydantic model for the *CSV content* might not be needed here,
# but you would define models if your real service returned JSON.