import streamlit as st
from configs import logger, log_verbose
from server.utils import get_httpx_client
from typing import Optional
from webui_pages.utils import ApiRequest
from io import BytesIO


speaker_dict = {
    'EN': ['EN-US', 'EN-BR', 'EN-AU', 'EN-INDIA', 'EN-DEFAULT'],
    'ES': ['ES'],
    'FR': ['FR'],
    'ZH': ['ZH'],
    'JP': ['JP'],
    'KR': ['KR'],
}

def text2audio_melo_page(api: ApiRequest, is_lite: bool = None):
    st.set_page_config(
        page_title="Text-To-Speech",
        page_icon="📕",
    )
    st.write("## Text-To-Speech")
    st.markdown(f"""
    - You can download the audio by clicking on the vertical three points next to the displayed audio widget.

    - The audio is synthesized by AI. 音频由AI合成，仅供参考。

    """, unsafe_allow_html=True)


    def text2audio(
        input: str,
        voice: str = 'ZH',
        prompt: Optional[str] = '',
        language: Optional[str] = 'ZH',
        model: Optional[str] = 'ZH',
        response_format: Optional[str] = 'wav',
        speed: Optional[float] = 1.0
    ) :
        try:
            address = "http://127.0.0.1:6007"
            with get_httpx_client() as client:
                r = client.post(address + "/v1/audio/speech",
                    json={"input": input, "prompt": prompt, "voice": voice, "response_format": response_format, "speed": speed, "language": language},
                )
                return BytesIO(r.content)
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e}',
                            exc_info=e if log_verbose else None)

    def new_line(i):
        content=st.text_area("Text to be synthesized into speech (合成文本)", "合成文本", key=f"{i}_text", height=100)
        col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5])
        with col1:
            lang=st.selectbox("Language (语言)", ["ZH","EN","FR","JP","KR", "ES"], key=f"{i}_lang")
        with col2:
            prompt=st.text_input(" (留空)", "", key=f"{i}_prompt")
        with col3:
            speed=st.selectbox("Speed (速度)", [1.0,1.5,0.7,2.0], key=f"{i}_speed")
        with col4:
            speaker=st.selectbox("Speaker(说话人)", speaker_dict[lang], key=f"{i}_speaker")
        with col5:
            format=st.selectbox("Format (音频格式)", ["wav", "mp3", "ogg"], key=f"{i}_format")
            
        flag = st.button(f"Synthesize (合成)", key=f"{i}_button1")
        if flag:
            sample_rate = 44100
            use_format = f"audio/{format}"
            st.audio(text2audio(content, prompt=prompt, response_format=format, language=lang, speed=float(speed), voice=speaker), sample_rate=sample_rate, format=use_format)
            # st.audio(path, sample_rate=config.sampling_rate)


    new_line(0)