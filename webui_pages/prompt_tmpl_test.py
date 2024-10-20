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
from configs import (TEMPERATURE, HISTORY_LEN, PROMPT_TEMPLATES,
                     DEFAULT_KNOWLEDGE_BASE, DEFAULT_SEARCH_ENGINE, SUPPORT_AGENT_MODEL)
from server.knowledge_base.utils import LOADER_DICT
from server.utils import get_prompt_template
import uuid
from typing import List, Dict

PROMPT_TMPLS = {
    "关键词提取": """你是一个关键词捕捉专家，请捕获用户问题中最关键的1到2个词（只要名词，不需要标点符号，不需要备注说明，直接给出关键词，结果用“、”分割）。
例如：
问题：使用shell工具查询当前系统的磁盘情况
关键词：磁盘、shell
问题：照壁有什么用
关键词：照壁
问题：使用arxiv工具查询关于transformer的论文
关键词：transformer、arxiv
问题：《红楼梦》是我国古代著名的长篇小说之一，它的别名是：
关键词：红楼梦、别名
问题：在我国风俗中，常常避讳73和84这两个岁数，因为这是两位历史人物去世的年龄，他们是
关键词：73、84、历史人物、年龄

下面是用户的问题：
问题：{{ text }}
关键词（只要名词，不需要标点符号，不需要备注说明，直接给出关键词，结果用“、”分割）：""",


    "summary1": """请简洁和专业的总结下面文档内容。文档内容如下：


"{text}"


文档总结为：""",


    "summary2": """<指令>请简洁和专业的总结下面文档内容。</指令>

<文档>"{text}"</文档>


文档总结为：""",


    "summary3":
            '请简洁和专业的总结下面文档内容。'
            '文档内容如下：\n'
            '\n\n{{ text }}\n\n'
            '文档总结为：\n',


    "summary4":
            '<指令>请简洁和专业的总结下面文档内容。</指令>\n'
            '<文档>{{ text }}</文档>\n',


    "summary_lc":
            """Write a concise summary of the following:


"{text}"


CONCISE SUMMARY:""",


    "summary_lc_zh":
            """Write a concise summary of the following:


"{text}"


CONCISE SUMMARY IN CHINESE:""",


    "refine":
            """\
Your job is to produce a final summary.
We have provided an existing summary up to a certain point: {existing_answer}
We have the opportunity to refine the existing summary (only if needed) with some more context below.
------------
{text}
------------
Given the new context, refine the original summary.
If the context isn't useful, return the original summary.\
""",


    "relate_qa": """根据以下内容，生成几个相关的提问。内容如下：


"{text}"


相关的提问：""",

}

PROMPT_TMPL_EG = {
    "关键词提取": ["""中国建筑有哪几个流派""", """
        都江堰和秦始皇陵哪个的修建年代更早？
        """, """
        林黛玉和贾宝玉的父母分别是谁？
        """],
}


chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def prompt_tmpl_test_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    conversation_id = st.session_state["conversation_ids"][chat_box.cur_chat_name]
    st.session_state.setdefault("file_chat_id", None)
    default_model = api.get_default_llm_model()[0]
    llm_model = "Qwen1.5-7B-Chat"  # "chatglm3-6b-32k" #

    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`FenghouAI-Chat`](https://shudi.yuque.com/ftc8lc/wiki) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    st.markdown(
        """
    <style>
        [data-testid="stSidebarNav"] {
            display: none
        }
        [data-testid="block-container"] {
            padding: 3rem 4rem 1rem;
        }
        [data-testid="stSidebarUserContent"] {
            padding: 30px 20px 20px 20px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Set the title of the demo
    # st.title("💬 园博园Chat")
    st.write("## 💬 提示词测试")
    # Add your custom text here, with smaller font size
    # st.markdown("<sub>园博园专用聊天（左边设置参数），例如： </sub> \n\n <sub> 例1：介绍一下园博园</sub> \n\n <sub> 例2：龙景书院</sub> \n\n <sub> 园博园主要建筑</sub> \n\n <sub> 园博园公厕</sub>", unsafe_allow_html=True)

    prompt_templates_kb_list = list(PROMPT_TMPLS.keys())
    prompt_template_name = prompt_templates_kb_list[0]
    if "prompt_template_select" not in st.session_state:
        st.session_state.prompt_template_select = prompt_templates_kb_list[0]

    def prompt_change():
        text = f"已切换为 {st.session_state.prompt_template_select} 模板。"
        st.toast(text)

    prompt_template_select = st.selectbox(
        "快捷选择Prompt模板：",
        prompt_templates_kb_list,
        index=0,
        on_change=prompt_change,
        key="prompt_template_select",
    )
    prompt_template_name = st.session_state.prompt_template_select
    prompt_template = PROMPT_TMPLS[prompt_template_name]
    system_prompt = st.text_area(
        label="System Prompt",
        height=500,
        value=prompt_template,
        key="system_prompt",
    )

    eg = PROMPT_TMPL_EG[prompt_template_name]
    prompt_eg = None
    if eg:
        numbers = [i for i in range(0, len(eg))]  # 生成1到9的数字列表
        prompt_eg_select = st.selectbox(
            "快捷输入：",
            numbers,
            index=0,
            key="prompt_eg_select",
        )
        prompt_eg = PROMPT_TMPLS[prompt_template_name][int(prompt_eg_select)]

    DEFAULT_SYSTEM_PROMPT = '''
    You are an AI programming assistant. Follow the user's instructions carefully. Respond using markdown.
    '''.strip()

    now = datetime.now()
    with st.sidebar:

        temperature = st.slider(
            'temperature', 0.0, 1.5, 0.95, step=0.01
        )

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = prompt_eg if prompt_eg else "请输入对话内容，换行请使用Shift+Enter"

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        chat_box.user_say(prompt)

        chat_box.ai_say("正在思考...")
        text = ""
        for d in api.chat_chat(prompt,
                              history=[],
                               conversation_id=conversation_id,
                               model=llm_model,
                               prompt_name=prompt_template_name,
                               system_prompt=system_prompt,
                               temperature=temperature):
            if error_msg := check_error_msg(d):  # check whether error occured
                st.error(error_msg)
            elif chunk := d.get("text"):
                text += chunk
                chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            # chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
