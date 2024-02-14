# -*- coding:utf-8 -*-
from enum import Enum
import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
import os
import re
import time
import json
from configs import (TEMPERATURE, HISTORY_LEN, PROMPT_TEMPLATES,
                     DEFAULT_KNOWLEDGE_BASE, DEFAULT_SEARCH_ENGINE, SUPPORT_AGENT_MODEL)
from server.knowledge_base.utils import LOADER_DICT
from server.utils import get_prompt_template
import uuid
from typing import List, Dict, Optional

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)



def tool_chat_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    default_model = api.get_default_llm_model()[0]
    llm_model = ""
    
    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`FenghouAI-Chat`](https://github.com) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    st.markdown(
        """
    <style>
        [data-testid="stSidebarNav"] {
            display: none
        }
        [data-testid="stSidebarUserContent"] {
            padding: 30px 20px 20px 20px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


    # Set the title of the demo
    st.title("💬 插件Chat")
    # Add your custom text here, with smaller font size
    st.markdown("<sub>插件专用聊天（左边选择插件）</sub>", unsafe_allow_html=True)
    #info_placeholder = st.empty()



    now = datetime.now()
    with st.sidebar:



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
        llm_model = st.selectbox("选择LLM模型：",
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
                r = api.change_llm_model(prev_model, llm_model)
                if msg := check_error_msg(r):
                    st.error(msg)
                elif msg := check_success_msg(r):
                    st.success(msg)
                    st.session_state["prev_llm_model"] = llm_model


        prompt_templates_kb_list = list(PROMPT_TEMPLATES["agent_chat"].keys())
        prompt_template_name = prompt_templates_kb_list[0]
        if "prompt_template_select" not in st.session_state:
            st.session_state.prompt_template_select = prompt_templates_kb_list[0]

        def prompt_change():
            text = f"已切换为 {st.session_state.prompt_template_select} 模板。"
            st.toast(text)

        prompt_template_select = st.selectbox(
            "请选择Prompt模板：",
            prompt_templates_kb_list,
            index=0,
            on_change=prompt_change,
            key="prompt_template_select",
        )
        prompt_template_name = st.session_state.prompt_template_select
        prompt_template = get_prompt_template("agent_chat", prompt_template_name)
        system_prompt = st.text_area(
            label="System Prompt",
            height=200,
            value=prompt_template,
            key="system_prompt",
        )
        temperature = st.slider(
            'temperature', 0.0, 1.0, 0.1, step=0.05
        )
        history_len = st.number_input("历史对话轮数：", 0, 20, HISTORY_LEN)
        
        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
    
    # Display chat messages from history on app rerun
    chat_box.output_messages()
    
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter"
    
    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
            history = get_messages_history(history_len)
            chat_box.user_say(prompt)

            if not any(agent in llm_model for agent in SUPPORT_AGENT_MODEL):
                chat_box.ai_say([
                    f"正在思考... \n\n <span style='color:red'>该模型并没有进行Agent对齐，请更换支持Agent的模型获得更好的体验！</span>\n\n\n",
                    Markdown("...", in_expander=True, title="思考过程", state="complete"),

                ])
            else:
                chat_box.ai_say([
                    f"正在思考...",
                    Markdown("...", in_expander=True, title="思考过程", state="complete"),

                ])
            text = ""
            ans = ""
            for d in api.agent_chat(prompt,
                                    history=history,
                                    model=llm_model,
                                    prompt_name=prompt_template_name,
                                    temperature=temperature,
                                    ):
                try:
                    d = json.loads(d)
                except:
                    pass
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)
                if chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=1)
                if chunk := d.get("final_answer"):
                    ans += chunk
                    chat_box.update_msg(ans, element_index=0)
                if chunk := d.get("tools"):
                    text += "\n\n".join(d.get("tools", []))
                    chat_box.update_msg(text, element_index=1)
                chat_box.update_msg(ans, element_index=0, streaming=False)
                chat_box.update_msg(text, element_index=1, streaming=False)


    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()



























