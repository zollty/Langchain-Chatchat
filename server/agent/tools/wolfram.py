# Langchain 自带的 Wolfram Alpha API 封装
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field

wolfram_alpha_appid = "PWV4W7-XXTQQ8YAGT"

def wolfram(query: str):
    wolfram = WolframAlphaAPIWrapper(wolfram_alpha_appid=wolfram_alpha_appid)
    ans = wolfram.run(query)
    return ans

class WolframInput(BaseModel):
    location: str = Field(description="需要运算的具体问题")