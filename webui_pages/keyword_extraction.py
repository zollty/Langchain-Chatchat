# -*- coding:utf-8 -*-
import streamlit as st
from webui_pages.utils import *

new_api_url = "http://127.0.0.1:20000"

def remote_api(
    sentence: str,
    model_name: str = None,
    max_tokens: Optional[int] = 2000,
    temperature: Optional[float] = 0.1,
) :
    try:
        address = new_api_url
        with get_httpx_client() as client:
            r = client.post(address + "/spchat/keyword_extraction",
                json={"sentence": sentence, "max_tokens": max_tokens, "model_name": model_name},
            )
            return r.json()
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)


def keyword_extraction_page(api: ApiRequest, is_lite: bool = False):
    st.set_page_config(layout="wide")

    st.markdown(
        """
    <style>
        [data-testid="block-container"] {
            padding: 3rem 4rem 1rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    default_input = """重庆园博园有哪些景点
中国建筑有哪几个流派
照壁有什么用
徽派建筑的特点是什么？
请问重庆渝北当前的气温
林黛玉和贾宝玉的父母分别是谁？
古人的婚礼在什么时间举行？
“弱冠”指的是男子多少岁？
《红楼梦》是我国古代著名的长篇小说之一，它的别名是：
中国历史上被誉为“药王“的是
都江堰和秦始皇陵哪个的修建年代更早？
从事贸易活动的人叫做“商人”，这跟历史上的商代有关吗？"""


    # Set the title of the demo
    st.write("## 关键词提取")
    # Add your custom text here, with smaller font size
    st.markdown("<sub>内置“关键词提取”的prompt。可用于知识库问答等场景</sub>", unsafe_allow_html=True)
    
    running_models = list(api.list_running_models())
    available_models = []
    config_models = api.list_config_models()
    if not is_lite:
        for k, v in config_models.get("local", {}).items(): # 列出配置了有效本地路径的模型
            if (v.get("model_path_exists")
                and k not in running_models):
                available_models.append(k)
    for k, v in config_models.get("online", {}).items():  # 列出ONLINE_MODELS中直接访问的模型
        if not v.get("provider") and k not in running_models:
            available_models.append(k)
    llm_models = running_models + available_models
    
    
    def llm_model_format_func(x):
        if x in running_models:
            return f"{x} (Running)"
        return x
    index = 0
    llm_model = st.selectbox("切换LLM模型（停止当前选中的Running模型，启动选中的未运行模型）：",
                                llm_models,
                                index,
                                format_func=llm_model_format_func,
                                key="llm_model",
                                )

    content=st.text_area("测试文本 (每行为一条)", default_input, key="input_text", height=300)

    if st.button(f"分词", key="button1"):
        submit_info = st.empty()
        submit_info.text("▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░正在处理中…………请稍等（勿重复点击）")
        sentences = content.split("\n")
        result = []
        for _, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            res = remote_api(sentence, model_name=llm_model)
            result.append("、".join(res))
        submit_info.empty()
        st.text_area("分词结果", "\n".join(result), key="result_text", height=300)
    


























