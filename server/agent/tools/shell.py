# LangChain 的 Shell 工具
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import ShellTool

def shell(query: str):
    tool = ShellTool()
    query = query.rstrip("\"").lstrip("\"").rstrip("`").lstrip("`")
    if query.startswith("rm ") or query.startswith("mv "):
        return "危险命令"
    return tool.run(tool_input=query)

class ShellInput(BaseModel):
    query: str = Field(description="一个能在Linux命令行运行的Shell命令")