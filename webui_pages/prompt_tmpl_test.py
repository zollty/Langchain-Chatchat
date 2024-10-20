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
from langchain.prompts import PromptTemplate

PROMPT_TMPLS = {
    "relate_qa": """根据以下内容，生成几个相关的提问。内容如下：


"{{ input }}"


相关的提问：""",


    "summary1": """请简洁和专业的总结下面文档内容。文档内容如下：


"{{ input }}"


文档总结为：""",


    "summary2": """<指令>请简洁和专业的总结下面文档内容。</指令>

<文档>"{{ input }}"</文档>


文档总结为：""",


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
问题：{{ input }}
关键词（只要名词，不需要标点符号，不需要备注说明，直接给出关键词，结果用“、”分割）：""",


    "summary3":
        '请简洁和专业的总结下面文档内容。'
        '文档内容如下：\n'
        '\n\n{{ input }}\n\n'
        '文档总结为：\n',


    "summary4":
        '<指令>请简洁和专业的总结下面文档内容。</指令>\n'
        '<文档>{{ input }}</文档>\n',


    "summary_lc":
        """Write a concise summary of the following:


"{{ input }}"


CONCISE SUMMARY:""",


    "summary_lc_zh":
        """Write a concise summary of the following:


"{{ input }}"


CONCISE SUMMARY IN CHINESE:""",


    "refine":
        """\
Your job is to produce a final summary.
We have provided an existing summary up to a certain point: {existing_answer}
We have the opportunity to refine the existing summary (only if needed) with some more context below.
------------
{{ input }}
------------
Given the new context, refine the original summary.
If the context isn't useful, return the original summary.\
""",


    "rag_search":
            '<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，答案请使用中文。 </指令>\n'
            '<已知信息>{{ context }}</已知信息>\n'
            '<问题>{{ question }}</问题>\n',


    "rag_fast": """使用 <Data></Data> 标记中的内容作为你的知识:

<Data>
{{ context }}
</Data>

回答要求：
- 如果你不清楚答案，你需要澄清。
- 避免提及你是从 <Data></Data> 获取的知识。
- 保持答案与 <Data></Data> 中描述的一致。
- 使用 Markdown 语法优化回答格式。

问题:\"\"\"{{ question }}\"\"\"""",


    "rag_youdao": """参考信息：
{{ context }}
---
我的问题或指令：
{{ question }}
---
请根据上述参考信息回答我的问题或回复我的指令。前面的参考信息可能有用，也可能没用，你需要从我给出的参考信息中选出与我的问题最相关的那些，来为你的回答提供依据。回答一定要忠于原文，简洁但不丢信息，不要胡乱编造。我的问题或指令是什么语种，你就用什么语种回复,
你的回复：""",


    "充当英语翻译和改进":
            '**替代**：语法，谷歌翻译\n\n> 我希望你能担任英语翻译、拼写校对和修辞改进的角色。我会用任何语言和你交流，你会识别语言，将其翻译并用更为优美和精炼的英语回答我。请将我简单的词汇和句子替换成更为优美和高雅的表达方式，确保意思不变，但使其更具文学性。请仅回答更正和改进的部分，不要写解释。第一个需要翻译的是：\n'
            '"{{ input }}"',

    "把任何语言翻译成中文":
        '下面我让你来充当翻译家，你的目标是把任何语言翻译成中文，请翻译时不要带翻译腔，而是要翻译得自然、流畅和地道，使用优美和高雅的表达方式。第一个需要翻译的是：\n'
        '"{{ input }}"',

    "把任何语言翻译成英语":
        '下面我让你来充当翻译家，你的目标是把任何语言翻译成英文，请翻译时不要带翻译腔，而是要翻译得自然、流畅和地道，使用优美和高雅的表达方式。第一个需要翻译的是：\n'
        '"{{ input }}"',

    "充当词典(附中文解释)":
        '将英文单词转换为包括中文翻译、英文释义和一个例句的完整解释。请检查所有信息是否准确，并在回答时保持简洁，不需要任何其他反馈。第一个单词是: \n'
        '"{{ input }}"',

    "充当旅游指南":
        '我想让你做一个旅游指南。我会把我的位置写给你，你会推荐一个靠近我的位置的地方。在某些情况下，我还会告诉您我将访问的地方类型。您还会向我推荐靠近我的第一个位置的类似类型的地方。我的第一个建议请求是: \n'
        '"{{ input }}"',

    "扮演脱口秀喜剧演员":
        '我想让你扮演一个脱口秀喜剧演员。我将为您提供一些与时事相关的话题，您将运用您的智慧、创造力和观察能力，根据这些话题创建一个例程。您还应该确保将个人轶事或经历融入日常活动中，以使其对观众更具相关性和吸引力。我的第一个请求是: \n'
        '"{{ input }}"',

    "二次元语气":
        'You are a helpful assistant. 请用二次元可爱语气回答问题。我的第一个请求是: \n'
        '"{{ input }}"',

    "充当医生":
        '我想让你扮演医生的角色，提出合理的治疗方法来治疗疾病。您应该能够推荐常规药物、草药和其他天然替代品。在提供建议时，您还需要考虑患者的年龄、生活方式和病史。我的第一个建议请求是：\n'
        '{{ input }}',

}

PROMPT_TMPL_EG = {
    "关键词提取": ["""中国建筑有哪几个流派""",
                   """都江堰和秦始皇陵哪个的修建年代更早？""",
                   """林黛玉和贾宝玉的父母分别是谁？"""],
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
    # st.session_state.setdefault("prompt", "")
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
    st.write("### 💬 提示词测试")
    # Add your custom text here, with smaller font size
    # st.markdown("<sub>园博园专用聊天（左边设置参数），例如： </sub> \n\n <sub> 例1：介绍一下园博园</sub> \n\n <sub> 例2：龙景书院</sub> \n\n <sub> 园博园主要建筑</sub> \n\n <sub> 园博园公厕</sub>", unsafe_allow_html=True)

    prompt_templates_kb_list = list(PROMPT_TMPLS.keys())
    prompt_template_name = prompt_templates_kb_list[0]
    if "prompt_template_select" not in st.session_state:
        st.session_state.prompt_template_select = prompt_templates_kb_list[0]

    def prompt_change():
        chat_box.reset_history()
        text = f"已切换为 {st.session_state.prompt_template_select} 模板。"
        st.toast(text)

    prompt_template_select = st.selectbox(
        "快捷选择Prompt模板：",
        prompt_templates_kb_list,
        index=0,
        on_change=prompt_change,
        key="prompt_template_select",
    )
    prompt_template = PROMPT_TMPLS[prompt_template_select]
    system_prompt = st.text_area(
        label="System Prompt",
        height=300,
        value=prompt_template,
        key="system_prompt",
    )

    DEFAULT_SYSTEM_PROMPT = '''
    You are an AI programming assistant. Follow the user's instructions carefully. Respond using markdown.
    '''.strip()

    now = datetime.now()
    with st.sidebar:

        temperature = st.slider(
            'temperature', 0.0, 1.5, 0.95, step=0.01
        )

        # def prompt_change2():
        #     st.session_state["prompt"] = st.session_state.prompt_eg_select

        prompt_eg = None
        if prompt_template_select in PROMPT_TMPL_EG:
            eg = PROMPT_TMPL_EG[prompt_template_select]
            numbers = [i for i in range(0, len(eg))]  # 生成1到9的数字列表
            prompt_eg_select = st.selectbox(
                "快捷输入：",
                numbers,
                index=0,
                # on_change=prompt_change2,
                key="prompt_eg_select",
            )
            prompt_eg = eg[int(prompt_eg_select)]

        cols = st.columns(1)
        if cols[0].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = prompt_eg if prompt_eg else ""

    prompt = st.text_area("测试文本", chat_input_placeholder, key="prompt", height=200)

    if st.button(f"发送", key="button1"):
        chat_box.reset_history()

        prompt_tmpl = PromptTemplate.from_template(template=system_prompt, template_format="jinja2")
        final_prompt = prompt_tmpl.format(input=prompt)
        # chat_box.user_say(final_prompt)
        chat_box.ai_say("正在思考...")
        text = ""
        for d in api.chat_chat(final_prompt,
                               history=[],
                               conversation_id=conversation_id,
                               model=llm_model,
                               temperature=temperature):
            if error_msg := check_error_msg(d):  # check whether error occured
                st.error(error_msg)
            elif chunk := d.get("text"):
                text += chunk
                chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            # chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
