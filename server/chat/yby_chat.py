from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from configs import (BING_SEARCH_URL, BING_SUBSCRIPTION_KEY, METAPHOR_API_KEY,
                     LLM_MODELS, SEARCH_ENGINE_TOP_K, TEMPERATURE,
                     TEXT_SPLITTER_NAME, OVERLAP_SIZE)
from fastapi import Body
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from text_splitter import ChineseRecursiveTextSplitter
from typing import List, Optional, Dict
from server.chat.utils import History
from langchain.docstore.document import Document
import json
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from markdownify import markdownify
import requests


# 读取原始文档
raw_documents_sanguo = TextLoader('/ai/apps/data/园博园参考资料.txt', encoding='utf-8').load()
raw_documents_xiyou = TextLoader('/ai/apps/data/园博园介绍.txt', encoding='utf-8').load()
raw_documents_fw = TextLoader('/ai/apps/data/园博园服务.txt', encoding='utf-8').load()
yby_src = raw_documents_sanguo + raw_documents_xiyou + raw_documents_fw

def knowledge_search(text, result_len=SEARCH_ENGINE_TOP_K, **kwargs):

    url = 'https://www.yuque.com/api/v2/repos/lvcto2/cf_records/docs/ke0oveoeianiemry'
    data = {}       
    headers={
        "X-Auth-Token": "QLErUdVHGs3SGJ8dblK3zkjMgHH6XCg5DvqYxH3a",
        "Content-Type": "application/json"
    }
    # 发起请求并获取响应
    response = requests.get(url, headers=headers)
    data = response.json()
    # print("=========================------------------------")
    data = data["data"]
    # print(data)
    
    url2 = 'https://www.yuque.com/api/v2/repos/lvcto2/cf_records/docs/qozaqv7deeg7n0ne'
    response2 = requests.get(url2, headers=headers)
    data2 = response2.json()
    # print("=========================22------------------------")
    data2 = data2["data"]
    # print(data2)
    
    url3 = 'https://www.yuque.com/api/v2/repos/lvcto2/cf_records/docs/scq2qgwbsbot3som'
    response3 = requests.get(url3, headers=headers)
    data3 = response3.json()
    # print("=========================333------------------------")
    data3 = data3["data"]
    # print(data3)

    docs = [{
        "extract": data["body"],
        "url":url,
        "title":data["title"],
    }]

    return docs


def search_engine(
    text: str,
    result_len: int = SEARCH_ENGINE_TOP_K,
    split_result: bool = False,
    chunk_size: int = 15000,
    chunk_overlap: int = OVERLAP_SIZE,
) -> List[Dict]:

    tdocs = knowledge_search(text, num_results=result_len, use_autoprompt=True)
    for x in tdocs:
        x["extract"] = markdownify(x["extract"])
    contents = tdocs

    # metaphor 返回的内容都是长文本，需要分词再检索
    if split_result:
        docs = [Document(page_content=x["extract"],
                        metadata={"link": x["url"], "title": x["title"]})
                for x in contents]
        separators = [
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ]
        text_splitter = RecursiveCharacterTextSplitter(separators,
                                                       chunk_size=chunk_size,
                                                       chunk_overlap=chunk_overlap)
        #text_splitter = ChineseRecursiveTextSplitter(keep_separator=True,
        #                                               is_separator_regex=True,
        #                                               chunk_size=chunk_size,
        #                                               chunk_overlap=chunk_overlap)
        splitted_docs = text_splitter.split_documents(docs)
        
        # 将切分好的文档放入临时向量库，重新筛选出TOP_K个文档
        if len(splitted_docs) > result_len:
            normal = NormalizedLevenshtein()
            for x in splitted_docs:
                x.metadata["score"] = normal.similarity(text, x.page_content)
            splitted_docs.sort(key=lambda x: x.metadata["score"], reverse=True)
            splitted_docs = splitted_docs[:result_len]

        docs = [{"snippet": x.page_content,
                "link": x.metadata["link"],
                "title": x.metadata["title"]}
                for x in splitted_docs]
    else:
        docs = [{"snippet": x["extract"],
                "link": x["url"],
                "title": x["title"]}
                for x in contents]

    return docs


def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(page_content=result["snippet"] if "snippet" in result.keys() else "",
                       metadata={"source": result["link"] if "link" in result.keys() else "",
                                 "filename": result["title"] if "title" in result.keys() else ""})
        docs.append(doc)
    return docs


async def lookup_search_engine2(
        query: str,
        top_k: int = SEARCH_ENGINE_TOP_K,
        split_result: bool = False,
):
    results = await run_in_threadpool(search_engine, query, result_len=top_k, split_result=split_result)
    docs = search_result2docs(results)
    return docs

async def lookup_search_engine(
        query: str,
        top_k: int = SEARCH_ENGINE_TOP_K,
        split_result: bool = False,
):
    return yby_src

async def yby_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                            top_k: int = Body(SEARCH_ENGINE_TOP_K, description="检索结果数量"),
                            history: List[History] = Body([],
                                                            description="历史对话",
                                                            examples=[[
                                                                {"role": "user",
                                                                "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                                {"role": "assistant",
                                                                "content": "虎头虎脑"}]]
                                                            ),
                            stream: bool = Body(False, description="流式输出"),
                            model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                            temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                            max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
                            prompt_name: str = Body("default",description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                            split_result: bool = Body(False, description="是否对搜索结果进行拆分（主要用于metaphor搜索引擎）")
                       ):

    history = [History.from_data(h) for h in history]

    async def yby_chat_iterator(query: str,
                                          top_k: int,
                                          history: Optional[List[History]],
                                          model_name: str = LLM_MODELS[0],
                                          prompt_name: str = prompt_name,
                                          ) -> AsyncIterable[str]:
        nonlocal max_tokens
        callback = AsyncIteratorCallbackHandler()
        if isinstance(max_tokens, int) and max_tokens <= 0:
            max_tokens = None

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        docs = await lookup_search_engine(query, top_k, split_result=split_result)
        context = "\n".join([doc.page_content for doc in docs])

        prompt_template = get_prompt_template("yby_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        source_documents = [
            f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
            for inum, doc in enumerate(docs)
        ]

        if len(source_documents) == 0:  # 没有找到相关资料（不太可能）
            source_documents.append(f"""<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>""")

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"docs": source_documents}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)
        await task

    return StreamingResponse(yby_chat_iterator(query=query,
                                                         top_k=top_k,
                                                         history=history,
                                                         model_name=model_name,
                                                         prompt_name=prompt_name),
                             media_type="text/event-stream")

