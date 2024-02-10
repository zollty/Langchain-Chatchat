import streamlit as st
from webui_pages.utils import *
from configs import (OVERLAP_SIZE, ZH_TITLE_ENHANCE)

def test_file_parse_page(api: ApiRequest, is_lite: bool = None):
    st.set_page_config(layout="wide")
    files = st.text_input(label="可解析的URL", value="")
    # cols = st.columns(4)
    # cols[0].text_input(label="URL", value="")
    # cols[1].button(
    #             "查询",
    #             use_container_width=False,
    #     )
    # cols[2].write("")
    # cols[3].write("")

    # with st.sidebar:
    with st.expander(
            "文本内容处理配置",
            expanded=True,
    ):
        cols = st.columns(4)
        chunk_size = cols[0].number_input("单段文本最大长度：", 1, 2000, 500)
        chunk_overlap = cols[1].number_input("相邻文本重合长度：", 0, chunk_size, OVERLAP_SIZE)
        cols[2].write("")
        cols[2].write("")
        zh_title_enhance = cols[2].checkbox("开启中文标题加强", ZH_TITLE_ENHANCE)
        start_size = cols[3].number_input("解析开始字符位置：", 0)

    if st.button(
            "提交进行解析测试",
            # use_container_width=True,
            disabled=(files == None),
    ):
        submit_info = st.empty()
        print("---------------------------开始上传…………")
        submit_info.text("▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░正在处理中…………请稍等（勿重复点击）")
        ret = api.test_parse_docs([files],
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap,
                                    start_size=start_size,
                                    zh_title_enhance=zh_title_enhance)
        print("---------------------------解析成功…………")
        submit_info.empty()
        if msg := check_success_msg(ret):
            st.toast(msg, icon="✔")
            st.divider()
            st.code(ret.get("data"), language="None", line_numbers=True)
        elif msg := check_error_msg(ret):
            st.toast(msg, icon="✖")
            st.divider()
            doc_info = st.text_area("出错的文档:", max_chars=None, key="doc_info", value=msg, help=None, on_change=None, args=None, kwargs=None)

