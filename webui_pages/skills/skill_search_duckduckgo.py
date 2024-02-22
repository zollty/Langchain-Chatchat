import streamlit as st
from webui_pages.utils import *
from server.chat.search_engine_chat import duckduckgo_search
from langchain.tools import DuckDuckGoSearchResults

def skill_search_duckduckgo_page(api: ApiRequest = None, is_lite: bool = None):
    st.markdown(
        """
    <style>
        code {
            white-space : pre-wrap !important;
            word-break: break-word;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.subheader("免费互联网搜索引擎工具")
    st.markdown("<h5>使用说明：</h5>\n\n 1、输入搜索关键字 \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")

    args = st.text_input(label="执行的命令：", value="Transformer", key="args")
    wron = st.toggle('使用Wrapper接口')
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        if wron:
            ret = duckduckgo_search(args)
        else:
            search = DuckDuckGoSearchResults()
            ret = search.run("args")
        st.code(ret, language="javascript", line_numbers=False)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n1、请勿频繁使用，免费API每日限制100次！！", unsafe_allow_html=True)
    st.divider()