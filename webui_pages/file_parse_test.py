import streamlit as st
from webui_pages.utils import *
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path, LOADER_DICT
from server.knowledge_base.kb_service.base import get_kb_details, get_kb_file_details
from typing import Literal, Dict, Tuple
from configs import (kbs_config,
                    EMBEDDING_MODEL, DEFAULT_VS_TYPE,
                    CHUNK_SIZE, OVERLAP_SIZE, ZH_TITLE_ENHANCE)
from server.utils import list_embed_models, list_online_embed_models
import os
import time
import json

def test_file_parse_page(api: ApiRequest, is_lite: bool = None):
    st.set_page_config(layout="wide")
    # 上传文件
    files = st.file_uploader("上传知识文件：(仅做文件解析，不保存数据！！)",
                                [i for ls in LOADER_DICT.values() for i in ls],
                                accept_multiple_files=False,
                                )
    # with st.sidebar:
    with st.expander(
            "文本内容处理配置",
            expanded=True,
    ):
        cols = st.columns(4)
        chunk_size = cols[0].number_input("单段文本最大长度：", 1, 2000, 500)
        chunk_overlap = cols[1].number_input("相邻文本重合长度：", 0, chunk_size, OVERLAP_SIZE)
        cols[2].write("")
        cols[2].write("")
        zh_title_enhance = cols[2].checkbox("开启中文标题加强", ZH_TITLE_ENHANCE)
        start_size = cols[3].number_input("解析开始字符位置：", 0)

    if st.button(
            "上传进行解析测试",
            # use_container_width=True,
            disabled=(files == None),
    ):
        submit_info = st.empty()
        print("---------------------------开始上传…………")
        submit_info.text("▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░正在处理中…………请稍等（勿重复点击）")
        ret = api.test_parse_docs([files],
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap,
                                    start_size=start_size,
                                    zh_title_enhance=zh_title_enhance)
        print("---------------------------上传成功…………")
        submit_info.empty()
        if msg := check_success_msg(ret):
            st.toast(msg, icon="✔")
            docs = [file["d"] for file in ret.get("data").get("files")]
            dtext = []
            for d in docs:
                dtext += [id["page_content"] for id in d]
            st.divider()
            total_len = len("".join(dtext))
            st.subheader(f"解析后的文档: （起止字符：{start_size} ~ {start_size + total_len}）")
            idx = 0
            for vak in dtext:
                # vak = "\n\n\n\n".join(dtext)
                idx += 1
                st.text(f"==第 {idx} 段==")
                st.code(vak, language="None", line_numbers=True)
            # doc_info = st.text_area("解析后的文档:", max_chars=None, key="doc_info", value=vak, height=het*40, help=None, on_change=None, args=None, kwargs=None)
        elif msg := check_error_msg(ret):
            st.toast(msg, icon="✖")
            vak = json.dumps(ret.get("data").get("failed_files"))
            st.divider()
            doc_info = st.text_area("出错的文档:", max_chars=None, key="doc_info", value=vak, help=None, on_change=None, args=None, kwargs=None)

