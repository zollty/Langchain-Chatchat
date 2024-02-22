import streamlit as st
from webui_pages.utils import *
from server.agent.tools.arxiv import arxiv

def skill_arxiv_page(api: ApiRequest = None, is_lite: bool = None):
    st.subheader("arxiv文献查询工具")
    st.markdown("<h5>使用说明：</h5>\n\n 1、用法示例1：1.234^5\n\n 2、用法示例2：10*23+12\n\n 3、用法示例3：sin(45) \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")

    args = st.text_input(label="执行的命令：", value="Transformer", key="args")
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        ret = arxiv(args)
        st.code(ret, language="None", line_numbers=True)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、请勿频繁使用，免费API每日限制100次</sub>", unsafe_allow_html=True)
    st.divider()