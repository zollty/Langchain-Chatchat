import streamlit as st
from configs import logger, log_verbose
from server.utils import get_httpx_client
from typing import Optional

st.set_page_config(
    page_title="demo page",
    page_icon="📕",
)
st.write("# Text-To-Speech")
st.markdown(f"""
### How to use:
         
- Simply select a **Speaker ID**, type in the **text** you want to convert and the emotion **Prompt**, like a single word or even a sentence. Then click on the **Synthesize** button below to start voice synthesis.

- You can download the audio by clicking on the vertical three points next to the displayed audio widget.

- For more information on **'Speaker ID'**, please consult the [EmotiVoice voice wiki page](https://github.com/netease-youdao/EmotiVoice/tree/main/data/youdao/text)

- The audio is synthesized by AI. 音频由AI合成，仅供参考。

""", unsafe_allow_html=True)


def text2audio(
    input: str,
    voice: str = '8051',
    prompt: Optional[str] = '',
    language: Optional[str] = 'zh_us',
    model: Optional[str] = 'emoti-voice',
    response_format: Optional[str] = 'mp3',
    speed: Optional[float] = 1.0
) :
    try:
        address = "http://127.0.0.1:6006"
        with get_httpx_client() as client:
            return client.post(address + "/v1/audio/speech",
                json={"input": input, "prompt": prompt, "voice": voice},
            )
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)

def new_line(i):
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 3.5, 1.3])
    with col1:
        speaker=st.selectbox("Speaker ID (说话人)", speakers, key=f"{i}_speaker")
    with col2:
        prompt=st.text_input("Prompt (开心/悲伤)", "", key=f"{i}_prompt")
    with col3:
        content=st.text_input("Text to be synthesized into speech (合成文本)", "合成文本", key=f"{i}_text")
    with col4:
        lang=st.selectbox("Language (语言)", ["zh_us"], key=f"{i}_lang")

    flag = st.button(f"Synthesize (合成)", key=f"{i}_button1")
    if flag:
        sample_rate = 44100
        st.audio(text2audio(content, prompt=prompt), sample_rate=sample_rate)
        # st.audio(path, sample_rate=config.sampling_rate)


new_line(0)