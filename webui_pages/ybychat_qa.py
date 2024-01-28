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
from typing import List, Dict

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



def yby_qa_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    st.session_state.setdefault("file_chat_id", None)
    default_model = api.get_default_llm_model()[0]
    llm_model = "chatglm3-6b-32k" # "Qwen-14B-Chat" #
    
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
    </style>
    """,
        unsafe_allow_html=True,
    )


    # Set the title of the demo
    st.title("💬 园博园Chat")
    # Add your custom text here, with smaller font size
    st.markdown("<sub>园博园专用聊天（左边设置参数），例如： </sub> \n\n <sub> 例1：介绍一下园博园</sub> \n\n <sub> 例2：龙景书院</sub> \n\n <sub> 园博园主要建筑</sub> \n\n <sub> 园博园公厕</sub>", unsafe_allow_html=True)

    DEFAULT_SYSTEM_PROMPT = '''
    You are an AI programming assistant. Follow the user's instructions carefully. Respond using markdown.
    '''.strip()

    now = datetime.now()
    with st.sidebar:
        
        prompt_templates_kb_list = list(PROMPT_TEMPLATES["yby_chat"].keys())
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
        prompt_template = get_prompt_template("yby_chat", prompt_template_name)
        system_prompt = st.text_area(
            label="System Prompt",
            height=200,
            value=prompt_template,
            key="system_prompt",
        )
        
        temperature = st.slider(
            'temperature', 0.0, 1.5, 0.95, step=0.01
        )
        history_len = st.number_input("历史对话轮数：", 0, 20, HISTORY_LEN)
        kb_top_k = st.number_input("匹配知识条数：", 1, 20, VECTOR_SEARCH_TOP_K)
        score_threshold = st.slider("知识匹配分数阈值：", 0.0, 2.0, float(SCORE_THRESHOLD), 0.01)
        
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

            chat_box.ai_say([
                f"正在查询知识库（请稍等）.....",
                Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
            ])
            text = ""
            d = api.chat_ydqa(prompt).json()
            print("--------------------------------------------")
            print(d["response"])
            if error_msg := check_error_msg(d):  # check whether error occured
                st.error(error_msg)
            elif chunk := d.get("response"):
                text += chunk
                chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            if sd := d.get("source_documents", []):
                sdc = [s["file_name"]+"-----------------------\n\n"+s["content"] for s in sd]
                chat_box.update_msg("\n\n\n\n".join(sdc), element_index=1, streaming=False)




























