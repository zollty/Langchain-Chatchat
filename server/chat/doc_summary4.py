from configs import (LLM_MODELS, TEMPERATURE)
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from server.chat.utils import History
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from typing import List, Optional, Dict
import json
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain


MAX_LENGTH = 30000

async def doc_chat_iterator(doc: str,
                            query: str = None,
                            stream: bool = False,
                            model_name: str = LLM_MODELS[0],
                            max_tokens: int = 0,
                            temperature: float = TEMPERATURE,
                            prompt_name: str = "summary1",
                            src_info=None,
                            ) -> AsyncIterable[str]:
    # 计算总长度
    total_length = len(doc)
    # 计算分段数量
    num_segments = (total_length // MAX_LENGTH) + 1

    if total_length < MAX_LENGTH:
        yield doc_chat_iterator2(doc=doc,
                            stream=stream,
                            model_name=model_name,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            prompt_name=prompt_name,
                            src_info=src_info)
        yield json.dumps({"src_info": src_info}, ensure_ascii=False)
    
    else:

        # 初始化分段列表
        segments = []

        # 遍历字符串，切割分段
        for i in range(num_segments):
            start = i * MAX_LENGTH
            end = min((i + 1) * MAX_LENGTH, total_length)
            segment = doc[start:end]
            segments.append(segment)

        # 打印分段
        idx = 0
        for segment in segments:
            idx += 1
            print("------------------------------------------------------")
            print(f"第{idx}段（{(idx - 1)*MAX_LENGTH}~{idx*MAX_LENGTH}字符）总结===\n\n")
            print(segment)
            yield json.dumps({"answer": f"第{idx}段（{(idx - 1)*MAX_LENGTH}~{idx*MAX_LENGTH}字符）总结===\n\n"}, ensure_ascii=False)
            yield doc_chat_iterator2(doc=segment,
                                stream=stream,
                                model_name=model_name,
                                max_tokens=max_tokens,
                                temperature=temperature,
                                prompt_name=prompt_name,
                                src_info=src_info)
            if stream:
                if idx==len(segments): 
                    yield json.dumps({"answer": "\n\n总结完成", "src_info": src_info}, ensure_ascii=False)
                else:
                    yield json.dumps({"answer": "\n\n"}, ensure_ascii=False)
            else:
                if idx==len(segments): 
                    yield json.dumps({"answer": "\n\n总结完成", "src_info": src_info}, ensure_ascii=False)
                else:
                    yield json.dumps({"answer": "\n\n"}, ensure_ascii=False)


async def doc_chat_iterator2(doc: str,
                            query: str = None,
                            stream: bool = False,
                            model_name: str = LLM_MODELS[0],
                            max_tokens: int = 0,
                            temperature: float = TEMPERATURE,
                            prompt_name: str = "summary1",
                            src_info=None,
                            ) -> AsyncIterable[str]:
    use_max_tokens = MAX_LENGTH
    if max_tokens > 0:
        use_max_tokens = max_tokens

    if len(doc) > MAX_LENGTH:
        doc = doc[:MAX_LENGTH]

    callback = AsyncIteratorCallbackHandler()
    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=use_max_tokens,
        callbacks=[callback],
    )

    prompt = PromptTemplate.from_template(get_prompt_template("doc_chat", prompt_name))
    # 注意这里是load_summarize_chain
    chain = load_summarize_chain(llm=model, chain_type="stuff", verbose=True, prompt=prompt)

    # Begin a task that runs in the background.
    task = asyncio.create_task(wrap_done(
        chain.acall([Document(page_content=doc)]),
        callback.done),
    )

    if stream:
        async for token in callback.aiter():
            yield json.dumps({"answer": token}, ensure_ascii=False)
        # yield json.dumps({"src_info": src_info}, ensure_ascii=False)
    else:
        answer = ""
        async for token in callback.aiter():
            answer += token
        yield json.dumps({"answer": answer}, ensure_ascii=False)
    
    await task