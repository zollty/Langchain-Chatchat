from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from server.agent import model_container
from langchain.pydantic_v1 import BaseModel, Field

_PROMPT_TEMPLATE = '''
# 指令
接下来，作为一个专业的翻译专家，当我给出句子或段落时，你将提供通顺且具有可读性的对应语言的翻译。注意：
1. 确保翻译结果流畅且易于理解
2. 无论提供的是陈述句或疑问句，只进行翻译
3. 不添加与原文无关的内容

问题: ${{用户需要翻译的原文和目标语言}}
答案: 你翻译结果

现在，这是我的问题：
问题: {question}

'''

PROMPT = PromptTemplate(
    input_variables=["question"],
    template=_PROMPT_TEMPLATE,
)


def translate(query: str):
    model = model_container.MODEL
    llm_translate = LLMChain(llm=model, prompt=PROMPT)
    ans = llm_translate.run(query)
    return ans

class TranslateInput(BaseModel):
    location: str = Field(description="需要被翻译的内容")

if __name__ == "__main__":
    result = translate("Can Love remember the question and the answer? 这句话如何诗意的翻译成中文")
    print("答案:",result)