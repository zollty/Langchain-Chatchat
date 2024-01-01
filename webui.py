import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages.dialogue.dialogue import dialogue_page, chat_box
from webui_pages.knowledge_base.knowledge_base import knowledge_base_page
from webui_pages.ybychat import yby_page
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
        "FuxiAI-Chat WebUI",
        os.path.join("img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com',
            'Report a bug': "https://github.com",
            'About': f"""欢迎使用 FuxiAI-Chat WebUI {VERSION}！"""
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
                "fuxi-chat-logo.png"
            ),
            use_column_width=True
        )
        st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
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


if __name__ == "__main__":
    router = StreamlitRouter()
    router.register(index, '/')
    router.register(test_page2, "/tasks/<int:x>", methods=['POST'])
    router.register(yby_chat_page, '/yby')
    # index(router)
    router.serve()
    

