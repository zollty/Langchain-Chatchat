import streamlit as st
from configs import logger, log_verbose
from server.utils import get_httpx_client
from typing import Optional
from webui_pages.utils import ApiRequest
from io import BytesIO
import base64

speaker_dict = {
    'EN': ['EN-Default', 'EN-US', 'EN-BR', 'EN-AU', 'EN_INDIA'],
    'ES': ['ES'],
    'FR': ['FR'],
    'ZH': ['ZH'],
    'JP': ['JP'],
    'KR': ['KR'],
}


def getaudio_html(mymidia_bytes):
    mymidia_str = "data:audio/ogg;base64,%s"%(base64.b64encode(mymidia_bytes).decode())
    return """
                    <audio autoplay class="stAudio">
                    <source src="%s" type="audio/ogg">
                    Your browser does not support the audio element.
                    </audio>
                """%mymidia_str

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
        default_txt = "曾经有一份真诚的爱情摆在我的面前，我没有珍惜，等到失去的时候才追悔莫及，人世间最痛苦的事情莫过于此。如果上天能够给我一个重新来过的机会，我会对那个女孩子说三个字：“我爱你”。如果非要给这份爱加上一个期限，我希望是——一~万~年。"
        content=st.text_area("Text to be synthesized into speech (合成文本)", default_txt, key=f"{i}_text", height=100)
        col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5])
        with col1:
            lang=st.selectbox("Language (语言)", ["ZH","EN","FR","JP","KR", "ES"], key=f"{i}_lang")
        with col2:
            speaker=st.selectbox("Speaker(说话人)", speaker_dict[lang], key=f"{i}_speaker")
        with col3:
            speed=st.selectbox("Speed (速度)", [1.0,1.2,0.8,1.5], key=f"{i}_speed")
        with col4:
            prompt=st.text_input(" (留空)", "", key=f"{i}_prompt")
        with col5:
            format=st.selectbox("Format (音频格式)", ["wav", "mp3", "ogg"], key=f"{i}_format")
            
        flag = st.button(f"Synthesize (合成)", key=f"{i}_button1")
        if flag:
            sample_rate = 44100
            use_format = f"audio/{format}"
            data = text2audio(content, prompt=prompt, response_format=format, language=lang, speed=float(speed), voice=speaker)
            st.audio(data, format=use_format)
            st.markdown(getaudio_html(data), unsafe_allow_html=True)
            # st.audio(path, sample_rate=config.sampling_rate)


    new_line(0)