from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class PreprocessingParameters(BaseModel):
    excludeMethods: Optional[List[str]] = None,
    removeBackground: bool = False,
    convertWavelengths: bool = False,