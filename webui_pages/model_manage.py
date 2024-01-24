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

def model_management_page(api: ApiRequest, is_lite: bool = None):
    st.markdown("<h4>使用说明：</h4>\n\n <sub>1、自定义Agent问答：为保证问答质量，需要手动切换成Qwen-14B模型</sub>\n\n <sub>2、知识库、园博园、搜索引擎问答：为保证问答质量，需要手动切换成chatglm3-6B-32k模型</sub>")
    default_model = api.get_default_llm_model()[0]
    def on_llm_change():
        if llm_model:
            config = api.get_model_config(llm_model)
            if not config.get("online_api"):  # 只有本地model_worker可以切换模型
                st.session_state["prev_llm_model"] = llm_model
            st.session_state["cur_llm_model"] = st.session_state.llm_model

    def llm_model_format_func(x):
        if x in running_models:
            return f"{x} (Running)"
        return x

    running_models = list(api.list_running_models())
    available_models = []
    config_models = api.list_config_models()
    if not is_lite:
        for k, v in config_models.get("local", {}).items(): # 列出配置了有效本地路径的模型
            if (v.get("model_path_exists")
                and k not in running_models):
                available_models.append(k)
    for k, v in config_models.get("online", {}).items():  # 列出ONLINE_MODELS中直接访问的模型
        if not v.get("provider") and k not in running_models:
            available_models.append(k)
    llm_models = running_models + available_models
    cur_llm_model = st.session_state.get("cur_llm_model", default_model)
    if cur_llm_model in llm_models:
        index = llm_models.index(cur_llm_model)
    else:
        index = 0
    llm_model = st.selectbox("切换LLM模型（停止当前选中的Running模型，启动选中的未运行模型）：",
                                llm_models,
                                index,
                                format_func=llm_model_format_func,
                                on_change=on_llm_change,
                                key="llm_model",
                                )
    if (st.session_state.get("prev_llm_model") != llm_model
            and not is_lite
            and not llm_model in config_models.get("online", {})
            and not llm_model in config_models.get("langchain", {})
            and llm_model not in running_models):
        with st.spinner(f"正在加载模型： {llm_model}，请勿进行操作或刷新页面"):
            prev_model = st.session_state.get("prev_llm_model")
            r = api.change_llm_model(prev_model, llm_model, keep_origin=False)
            if msg := check_error_msg(r):
                st.error(msg)
            elif msg := check_success_msg(r):
                st.success(msg)
                st.session_state["prev_llm_model"] = llm_model

    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、模型切换停止后，要稍等5~15秒才会变更Running状态</sub>")