import streamlit as st
from webui_pages.utils import *
from server.agent.tools.wolfram import wolfram

def skill_wolfram_page(api: ApiRequest = None, is_lite: bool = None):
    st.subheader("在线科学计算（wolfram）工具")
    st.markdown("<h5>使用说明：</h5>\n\n <sub>1、自定义Agent问答：为保证问答质量，需要手动切换成Qwen-14B模型</sub>\n\n <sub>2、知识库、园博园、搜索引擎问答：为保证问答质量，需要手动切换成chatglm3-6B-32k模型</sub> \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")
    args = st.text_input(label="执行的命令：（高级函数、方程式）", value="10th derivative of 1/(1+x)", key="args")
    st.markdown("用法示例：https://wenku.so.com/d/4e0aeccf51fd04a19dda9784c720ebc5")
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        ret = wolfram(args)
        st.code(ret, language="None", line_numbers=True)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、请勿执行危险命令</sub>", unsafe_allow_html=True)
    st.divider()