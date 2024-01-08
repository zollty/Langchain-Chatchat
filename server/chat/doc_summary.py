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

async def doc_chat_iterator(doc: str,
                            query: str = None,
                            stream: bool = False,
                            model_name: str = LLM_MODELS[0],
                            max_tokens: int = 0,
                            temperature: float = TEMPERATURE,
                            prompt_name: str = "summary1",
                            src_info=None,
                            ) -> AsyncIterable[str]:
    
    use_max_tokens = None
    if max_tokens > 0:
        use_max_tokens = max_tokens

    callback = AsyncIteratorCallbackHandler()
    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=use_max_tokens,
        callbacks=[callback],
    )

    prompt_template = get_prompt_template("doc_chat", prompt_name)
    input_msg = History(role="user", content=prompt_template).to_msg_template(False)
    chat_prompt = ChatPromptTemplate.from_messages([input_msg])

    chain = LLMChain(prompt=chat_prompt, llm=model)

    max_length = 12767
    if len(doc) < max_length:
        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": doc, "question": query}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"src_info": src_info}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer, "src_info": src_info}, ensure_ascii=False)
        
        await task
    else:

        # 计算总长度
        total_length = len(doc)
        # 计算分段数量
        num_segments = total_length // max_length

        # 初始化分段列表
        segments = []

        # 遍历字符串，切割分段
        for i in range(num_segments):
            start = i * max_length
            end = min((i + 1) * max_length, total_length)
            segment = doc[start:end]
            segments.append(segment)

        # 打印分段
        idx = 0
        for segment in segments:
            idx += 1
            # Begin a task that runs in the background.
            task = asyncio.create_task(wrap_done(
                chain.acall({"context": segment, "question": query}),
                callback.done),
            )

            yield json.dumps({"answer": f"第{idx}段（{(idx - 1)*max_length}~{idx*max_length}字符）总结===\n\n"}, ensure_ascii=False)
            if stream:
                async for token in callback.aiter():
                    # Use server-sent-events to stream the response
                    yield json.dumps({"answer": token}, ensure_ascii=False)
                yield json.dumps({"src_info": src_info}, ensure_ascii=False)
            else:
                answer = ""
                async for token in callback.aiter():
                    answer += token
                yield json.dumps({"answer": answer, "src_info": src_info}, ensure_ascii=False)
            
            await task



