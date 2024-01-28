import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages.dialogue.dialogue import dialogue_page, chat_box
from webui_pages.knowledge_base.knowledge_base import knowledge_base_page
from webui_pages.ybychat import yby_page
from webui_pages.ybychat_qa import yby_qa_page
from webui_pages.file_chat import file_chat_page
from webui_pages.file_parse_test import test_file_parse_page
from webui_pages.model_manage import model_management_page
import os
import sys
from configs import VERSION
from server.utils import api_address

from streamlit_router import StreamlitRouter


api = ApiRequest(base_url=api_address())

def index2(router):
    st.text(f"xxxxxx fron page create task")
    st.text("others on page create task")


def index(router):
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "FenghouAI-Chat WebUI",
        os.path.join("img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com',
            'Report a bug': "https://github.com",
            'About': f"""欢迎使用 FenghouAI-Chat WebUI {VERSION}！"""
        }
    )

    pages = {
        "对话": {
            "icon": "chat",
            "func": dialogue_page,
        },
        "知识库管理": {
            "icon": "hdd-stack",
            "func": knowledge_base_page,
        },
    }

    with st.sidebar:
        st.image(
            os.path.join(
                "img",
                "fenghou-banner.png"
            ),
            use_column_width=True
        )
        # st.caption(
        #     f"""<p align="right">当前版本：{VERSION}</p>""",
        #     unsafe_allow_html=True,
        # )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](api=api, is_lite=is_lite)


# variable router auto inject if as first params
def test_page2(x, router):
	st.text(f"POSTTTTT fron page create task x={x}")
	if st.button("back to index"):
		router.redirect(*router.build("index"))
	st.text("others on page create task")

def yby_chat_page(router):
	is_lite = "lite" in sys.argv
	yby_page(api=api, is_lite=is_lite)

def ybyqa_page(router):
	is_lite = "lite" in sys.argv
	api2 = ApiRequest(base_url="http://172.16.8.91:8777")
	yby_qa_page(api=api2, is_lite=is_lite)

def filechat_page(router):
	is_lite = "lite" in sys.argv
	file_chat_page(api=api, is_lite=is_lite)

def test_fileparse_page(router):
	is_lite = "lite" in sys.argv
	test_file_parse_page(api=api, is_lite=is_lite)

def model_manage_page(router):
	is_lite = "lite" in sys.argv
	model_management_page(api=api, is_lite=is_lite)

if __name__ == "__main__":
    router = StreamlitRouter()
    router.register(index, '/')
    router.register(test_page2, "/tasks/<int:x>", methods=['POST'])
    router.register(yby_chat_page, '/yby')
    router.register(filechat_page, '/fchat')
    router.register(test_fileparse_page, '/ftest')
    router.register(model_manage_page, '/modelmg')
    router.register(ybyqa_page, '/ybyqa')
    # index(router)
    router.serve()
    

