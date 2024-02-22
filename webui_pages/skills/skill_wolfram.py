import streamlit as st
from webui_pages.utils import *
from server.agent.tools.wolfram import wolfram

def skill_wolfram_page(api: ApiRequest = None, is_lite: bool = None):
    st.subheader("在线科学计算（wolfram）工具")
    st.markdown("<h5>使用说明：</h5>\n\n 1、用法示例1：integrate x sin(x^2)\n\n 2、用法示例2：10th derivative of 1/(1+x)\n\n 3、支持高级函数、方程式等\n\n 4、更多示例：https://www.wolframalpha.com/calculators/integral-calculator \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")
    args = st.text_input(label="执行的命令：", value="10th derivative of 1/(1+x)", key="args")
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        ret = wolfram(args)
        st.code(ret, language="None", line_numbers=True)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、请勿频繁使用，免费API每日限制100次</sub>", unsafe_allow_html=True)
    st.divider()