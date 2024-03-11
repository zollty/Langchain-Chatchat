
from langchain.docstore.document import Document
from langchain_core.pydantic_v1 import Field

class DocumentWithVSId(Document):
    """
    矢量化后的文档
    """
    id: str = Field(None, description="API data")
    score: float = Field(3.0, description="API data")
