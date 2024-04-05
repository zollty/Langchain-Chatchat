# -*- coding:utf-8 -*-
from enum import Enum
import streamlit as st
from webui_pages.utils import *
import uuid
from typing import List, Dict

new_api_url = "http://127.0.0.1:20000"

def remote_api(
    sentence: str,
    model_name: str = None,
    max_tokens: Optional[int] = 2000,
    temperature: Optional[float] = 0.1,
) :
    try:
        address = new_api_url
        with get_httpx_client() as client:
            r = client.post(address + "/spchat/keyword_extraction",
                data={"sentence": sentence},
            )
            return r.json()
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)


def keyword_extraction_page(api: ApiRequest, is_lite: bool = False):
    st.set_page_config(layout="wide")

    # st.markdown(
    #     """
    # <style>
    #     [data-testid="stSidebarNav"] {
    #         display: none
    #     }
    # </style>
    # """,
    #     unsafe_allow_html=True,
    # )


    # Set the title of the demo
    st.write("## 知识库问答分词工具")
    # Add your custom text here, with smaller font size
    st.markdown("<sub>内置分词的提示词</sub>", unsafe_allow_html=True)

    content=st.text_area("测试文本 (每行为一条)", "园博园有哪些景点", key="input_text", height=300)

    if st.button(f"分词", key="button1"):
        sentences = content.split("\n")
        result = []
        for _, sentence in enumerate(sentences):
            res = remote_api(sentence)
            print(res)
            result.append(res["data"])
        st.text_area("分词结果", result.join("\n"), key="result_text", height=300)
    


























