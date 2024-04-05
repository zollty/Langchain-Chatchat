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
                json={"sentence": sentence, "max_tokens": max_tokens},
            )
            return r.json()
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)


def keyword_extraction_page(api: ApiRequest, is_lite: bool = False):
    st.set_page_config(layout="wide")

    st.markdown(
        """
    <style>
        [data-testid="block-container"] {
            padding: 3rem 1rem 1rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    default_input = """重庆园博园有哪些景点
中国建筑有哪几个流派
照壁有什么用
徽派建筑的特点是什么？
请问重庆渝北当前的气温
林黛玉和贾宝玉的父母分别是谁？
古人的婚礼在什么时间举行？
“弱冠”指的是男子多少岁？
《红楼梦》是我国古代著名的长篇小说之一，它的别名是：
中国历史上被誉为“药王“的是
都江堰和秦始皇陵哪个的修建年代更早？
从事贸易活动的人叫做“商人”，这跟历史上的商代有关吗？
    """


    # Set the title of the demo
    st.write("## 知识库问答分词工具")
    # Add your custom text here, with smaller font size
    st.markdown("<sub>内置分词的提示词</sub>", unsafe_allow_html=True)

    content=st.text_area("测试文本 (每行为一条)", default_input, key="input_text", height=300)

    if st.button(f"分词", key="button1"):
        submit_info = st.empty()
        submit_info.text("▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░正在处理中…………请稍等（勿重复点击）")
        sentences = content.split("\n")
        result = []
        for _, sentence in enumerate(sentences):
            res = remote_api(sentence)
            result.append("、".join(res))
        submit_info.empty()
        st.text_area("分词结果", "\n".join(result), key="result_text", height=300)
    


























