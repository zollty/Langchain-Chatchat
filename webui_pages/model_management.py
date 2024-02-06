import streamlit as st
from webui_pages.utils import *
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from typing import Literal, Dict, Tuple
import os
import time


# SENTENCE_SIZE = 100

cell_renderer = JsCode("""function(params) {if(params.value==true){return '✓'}else{return '×'}}""")


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        wrapText=True, autoHeight=True
    )
    cell_renderer = JsCode("""
    function(params) {
    return params.value.replaceAll("\\n","<br/>"); // here is the key point
    }
    """)
    # , cellRenderer=cell_renderer
    gb.configure_column("desc", editable=True, maxWidth=500, cellStyle={"white-space": 'pre'}) #cellStyle={"white-space": 'pre'}
    gb.configure_column("usage", editable=True, maxWidth=240, cellStyle={"white-space": 'pre'})
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    gb.configure_pagination(
        enabled=True,
        paginationAutoPageSize=False,
        paginationPageSize=10
    )
    return gb


def get_kb_file_details() -> List[Dict]:
    data = []
    data.append({
            "name": "chatglm3-6b-32k",
            "status": "Running",
            "gpm_mem": "14G ~ 26G",
            "desc": """1、更强大的基础模型：使用了 GLM 混合目标函数，经过了人类偏好对齐训练等，评测性能大幅提升，
            在语义、数学、推理、代码、知识等不同角度的数据集上均有很好表现。
2、更高效的推理、更低的显存占用：几乎可以秒回，速度比ChatGPT还快！
3、更长的上下文：基座上下文长度（Context Length）由 初代的 2K 扩展到了 32K，支持8K上下文多轮对话！长对话模型增加到了32K！
4、更优秀的模型特性：原生支持工具调用……等复杂场景，胜任AI编程助手……
""",
            "usage": """1、综合能力均匀
2、可调教用于部分Agent
3、性能较好
""",
            "base_url": "http://192.168.16.104:21000/",
            "switch_": True,
        })

    data.append({
            "name": "Qwen-1.8B-Chat",
            "status": "Running",
            "gpm_mem": "4G ~ 10G",
            "desc": """1、 Qwen-Chat具备聊天、文字创作、摘要、信息抽取、翻译等能力，同时还具备一定的代码生成和简单数学推理的能力
2、新版还增强了 Qwen-72B-Chat 和 Qwen-1.8B-Chat 的系统指令（System Prompt）功能。……
""",
            "usage": """1、显存占用低
2、可调教用于部分Agent
3、知识量小，回答效果一般
""",
            "base_url": "http://192.168.16.104:21001/",
            "switch_": True,
        })

    data.append({
            "name": "Qwen-7B-Chat",
            "status": "Ready",
            "gpm_mem": "16G ~ 32G",
            "desc": """1、覆盖多语言（当前以中文和英文为主），总量高达3万亿token。
2、在相关基准评测中，Qwen系列模型拿出非常有竞争力的表现，显著超出同规模模型并紧追一系列最强的商业闭源模型。
3、 Qwen-Chat具备聊天、文字创作、摘要、信息抽取、翻译等能力，同时还具备一定的代码生成和简单数学推理的能力。
4、 还针对LLM对接外部系统等方面针对性地做了优化，当前具备较强的工具调用能力，以及最近备受关注的Code Interpreter的能力和扮演Agent的能力。
""",
            "usage": """1、综合能力均匀
2、用于Agent效果比较好
3、token长度只有4k
""",
            "base_url": "http://192.168.16.104:21002/",
            "switch_": False,
        })
    
    data.append({
            "name": "Qwen-14B-Chat",
            "status": "Support",
            "gpm_mem": "34G ~ 56G",
            "desc": """1、新版Qwen-14B-Chat模型用了更多训练数据（2.4T tokens），序列长度从2048扩展至8192。整体中文能力以及代码能力均有所提升。
2、更高效的推理、更低的显存占用：几乎可以秒回，速度比ChatGPT还快！
3、更长的上下文：基座上下文长度（Context Length）由 初代的 2K 扩展到了 32K，支持8K上下文多轮对话！长对话模型增加到了32K！
4、更优秀的模型特性：原生支持工具调用……等复杂场景，胜任AI编程助手……
""",
            "usage": """1、综合能力非常不错
2、用于Agent效果比较好
3、token长度只有4k
""",
            "base_url": "http://192.168.16.104:21003/",
            "switch_": False,
        })
    
    data.append({
            "name": "Qwen-14B-Chat-Int8",
            "status": "Ready",
            "gpm_mem": "26G ~ 40G",
            "desc": """1、更强大的基础模型：使用了 GLM 混合目标函数，经过了人类偏好对齐训练等，评测性能大幅提升，
            在语义、数学、推理、代码、知识等不同角度的数据集上均有很好表现。
2、更高效的推理、更低的显存占用：几乎可以秒回，速度比ChatGPT还快！
3、更长的上下文：基座上下文长度（Context Length）由 初代的 2K 扩展到了 32K，支持8K上下文多轮对话！长对话模型增加到了32K！
4、更优秀的模型特性：原生支持工具调用……等复杂场景，胜任AI编程助手……
""",
            "usage": """1、综合能力与非量化差距不大
2、用于Agent效果比较好
3、token长度只有4k
""",
            "base_url": "http://192.168.16.104:21004/",
            "switch_": False,
        })
    
    data.append({
            "name": "Qwen-72B-Chat-Int8",
            "status": "Support",
            "gpm_mem": "65G ~ 90+G",
            "desc": """1、更强大的基础模型：使用了 GLM 混合目标函数，经过了人类偏好对齐训练等，评测性能大幅提升，
            在语义、数学、推理、代码、知识等不同角度的数据集上均有很好表现。
2、Qwen-72B在所有任务上均超越了LLaMA2-70B的性能，同时在10项任务中的7项任务中超越GPT-3.5！
3、更长的上下文：基座上下文长度（Context Length）由 初代的 2K 扩展到了 32K，支持8K上下文多轮对话！长对话模型增加到了32K！
4、最新推出了 Qwen-72B 和 Qwen-72B-Chat，它们在 3T tokens上进行训练，并支持 32k 上下文。
""",
            "usage": """1、综合能力优秀
2、中文理解能力超越GPT-3.5！（评测+实测）
3、用于Agent效果比较好
4、token长度支持32K
""",
            "base_url": "http://192.168.16.104:21005/",
            "switch_": False,
        })

    return data


def model_portal_page(api: ApiRequest, is_lite: bool = None):
    # st.set_page_config(layout="wide")
    st.markdown(
        """
    <style>
        [data-testid="stSidebarUserContent"] {
            padding: 30px 20px 20px 20px;
        }
        [data-testid="block-container"] {
            padding-top: 40px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    llm_status_list = ["Running", "Ready", "Support"]
    llm_status = cols[0].selectbox(label="",
                                options=llm_status_list,
                                 key="llm_status",
                                 label_visibility="collapsed"
                                 )
    
    cols[1].write("")
    cols[2].text_input(label="", value="",
                       label_visibility="collapsed")
    cols[3].button(
                "查询",
                use_container_width=False,
        )

    kb = "test_yby"

    # 知识库详情
    # st.info("请选择文件，点击按钮进行操作。")
    doc_details = pd.DataFrame(get_kb_file_details())
    if not len(doc_details):
        st.info(f"知识库 `{kb}` 中暂无文件")
    else:
        # st.write(f"知识库 `{kb}` 中已有文件:")
        # st.info("知识库中包含源文件与向量库，请从下表中选择文件后操作")
        # doc_details.drop(columns=["kb_name"], inplace=True)
        doc_details = doc_details[[
            "name", "status", "gpm_mem", "desc", "usage", "base_url", "switch_",
        ]]
        gb = config_aggrid(
            doc_details,
            {
                ("name", "模型名称"): {},
                ("status", "运行状态"): {},
                ("gpm_mem", "显存需求"): {},
                ("desc", "模型简介"): {},
                ("usage", "使用建议"): {},
                ("base_url", "服务基础地址"): {},
                ("switch_", "运行控制"): {"cellRenderer": cell_renderer},
                # ("in_db", "向量库"): {"cellRenderer": cell_renderer},
            },
            "multiple",
        )

        MIN_HEIGHT = 200
        MAX_HEIGHT = 1000
        ROW_HEIGHT = 166

        doc_grid = AgGrid(
            doc_details,
            gb.build(),
            columns_auto_size_mode="FIT_CONTENTS",
            theme="alpine",
            custom_css={
                "#gridToolBar": {"display": "none"},
            },
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            height=MIN_HEIGHT + len(doc_details) * ROW_HEIGHT,
        )

