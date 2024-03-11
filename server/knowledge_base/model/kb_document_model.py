
from typing import Dict
from langchain.docstore.document import Document
from langchain_core.pydantic_v1 import Field, root_validator

class DocumentWithVSId(Document):
    """
    矢量化后的文档
    """
    id: str = Field(None, description="API data")
    score: float = Field(3.0, description="API data")
    
    @root_validator(pre=True)
    def validate_config(cls, v: Dict) -> Dict:
        pass
