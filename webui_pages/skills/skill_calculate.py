import streamlit as st
from webui_pages.utils import *
from server.agent.tools.calculate import calculate
from configs import LLM_MODELS, TEMPERATURE, Agent_MODEL
from server.utils import get_ChatOpenAI
from server.agent import model_container

def skill_calculate_page(api: ApiRequest = None, is_lite: bool = None):

    if Agent_MODEL:
        ## 如果有指定使用Agent模型来完成任务
        model_name=Agent_MODEL
    else:
        model_name=LLM_MODELS[0]
    
    model_container.MODEL = get_ChatOpenAI(model_name=model_name, temperature=TEMPERATURE)

    st.subheader("数学计算(numexpr)工具")
    st.text("依赖Agent模型：建议用（Qwen）")
    st.markdown("<h5>使用说明：</h5>\n\n 1、用法示例1：1.234^5\n\n 2、用法示例2：10*23+12\n\n 3、用法示例3：sin(45) \n\n", unsafe_allow_html=True)
    st.text("↓↓↓↓↓")

    args = st.text_input(label="执行的命令：", value="sin(45)", key="args")
    if st.button(
                "运行",
                disabled=(args == None),
                use_container_width=False,
        ):
        print("-------------------------")
        ret = calculate(args)
        st.code(ret, language="None", line_numbers=True)

    st.text("↑↑↑↑↑↑")
    st.markdown("<h4>注意事项：</h4>\n\n<sub>1、请勿执行危险命令</sub>", unsafe_allow_html=True)
    st.divider()