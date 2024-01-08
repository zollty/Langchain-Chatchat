from configs import (LLM_MODELS, TEMPERATURE)
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
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
    chat_prompt = PromptTemplate.from_template(prompt_template)

    chain = LLMChain(prompt=chat_prompt, llm=model)

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



