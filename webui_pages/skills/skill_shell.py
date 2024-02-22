import streamlit as st
from webui_pages.utils import *
from server.agent.tools.shell import shell

def skill_shell_page(api: ApiRequest = None, is_lite: bool = None):
    st.subheader("SHELL命令调用工具")
    st.markdown("<h5>使用说明：</h5>\n\n 1、用法示例1：df -lh\n\n 2、用法示例2：free -h\n\n 3、用法示例3：ls -lh /usr \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")

    args = st.text_input(label="执行的命令：", value="df -h", key="args")
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        ret = shell(args)
        st.code(ret, language="None", line_numbers=True)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、请勿执行危险命令</sub>", unsafe_allow_html=True)
    st.divider()