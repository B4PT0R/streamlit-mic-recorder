import os
import streamlit as st
import streamlit.components.v1 as components
import base64
from speech_recognition import Recognizer,AudioData

_RELEASE = True

state=st.session_state

if not '_last_audio_id' in state:
    state._last_audio_id=0

if not _RELEASE:
    _component_func = components.declare_component("streamlit_mic_recorder",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_mic_recorder", path=build_dir)

def mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording",just_once=False,use_container_width=False,key=None):
    component_value = _component_func(start_prompt=start_prompt,stop_prompt=stop_prompt,use_container_width=use_container_width,key=key,default=None)
    if component_value is None:
        return None
    else:
        id=component_value["id"]
        audio_bytes=base64.b64decode(component_value["audio_base64"])
        sample_rate=component_value["sample_rate"]
        sample_width=component_value["sample_width"]
        if id>state._last_audio_id or just_once==False:
            state._last_audio_id=id
            return {"bytes":audio_bytes,"sample_rate":sample_rate,"sample_width":sample_width}
        else: 
            return None
    
def speech_to_text(start_prompt="Start recording",stop_prompt="Stop recording",just_once=False,use_container_width=False,language='en',key=None):
    audio = mic_recorder(start_prompt=start_prompt,stop_prompt=stop_prompt,just_once=just_once,use_container_width=use_container_width,key=key)
    if audio is None:
        return None
    else:
        r = Recognizer()
        audio_data = AudioData(audio['bytes'],audio['sample_rate'],audio['sample_width'])
        try:
            text = r.recognize_google(audio_data,language=language)
            return text
        except:
            return ""

if not _RELEASE:
    import streamlit as st
    #from streamlit_mic_recorder import mic_recorder,speech_to_text
    
    state=st.session_state

    if 'text_received' not in state:
        state.text_received=[]

    c1,c2=st.columns(2)
    with c1:
        st.write("Convert speech to text:")
    with c2:
        text=speech_to_text(language='en',use_container_width=True,just_once=True,key='STT')
    
    if text:       
        state.text_received.append(text)

    for text in state.text_received:
        st.text(text)
    
    st.write("Record your voice, and play the recorded audio:")
    audio=mic_recorder(start_prompt="⏺️",stop_prompt="⏹️",key='recorder')

    if audio:       
        st.audio(audio['bytes'])
    


    
