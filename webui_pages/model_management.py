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
    gb.configure_column("No", width=40)
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
    result = {}
    kb_name = "test_yby"
    files_in_folder = ["aaa.txt", "bbb.pdf","ccc.txt", "dddd.pdf","eee.txt", "ffff.pdf"]
    for doc in files_in_folder:
        result[doc] = {
            "kb_name": kb_name,
            "file_name": doc,
            "file_ext": os.path.splitext(doc)[-1],
            "file_version": 0,
            "document_loader": "RapidOCRPDFLoader",
            "docs_count": 120,
            "text_splitter": "ChineseRecursiveTextSplitter",
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }

    data = []
    for i, v in enumerate(result.values()):
        v['No'] = i + 1
        data.append(v)

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

    kb = "test_yby"

    # 知识库详情
    # st.info("请选择文件，点击按钮进行操作。")
    doc_details = pd.DataFrame(get_kb_file_details())
    if not len(doc_details):
        st.info(f"知识库 `{kb}` 中暂无文件")
    else:
        st.write(f"知识库 `{kb}` 中已有文件:")
        st.info("知识库中包含源文件与向量库，请从下表中选择文件后操作")
        doc_details.drop(columns=["kb_name"], inplace=True)
        doc_details = doc_details[[
            "No", "file_name", "document_loader", "text_splitter", "docs_count", "in_folder", "in_db",
        ]]
        gb = config_aggrid(
            doc_details,
            {
                ("No", "序号"): {},
                ("file_name", "文档名称"): {},
                # ("file_ext", "文档类型"): {},
                # ("file_version", "文档版本"): {},
                ("document_loader", "文档加载器"): {},
                ("docs_count", "文档数量"): {},
                ("text_splitter", "分词器"): {},
                # ("create_time", "创建时间"): {},
                ("in_folder", "源文件"): {"cellRenderer": cell_renderer},
                ("in_db", "向量库"): {"cellRenderer": cell_renderer},
            },
            "multiple",
        )

        doc_grid = AgGrid(
            doc_details,
            gb.build(),
            columns_auto_size_mode="FIT_CONTENTS",
            theme="alpine",
            custom_css={
                "#gridToolBar": {"display": "none"},
            },
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False
        )

