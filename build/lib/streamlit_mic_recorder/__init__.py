import os
import streamlit as st
import streamlit.components.v1 as components
import base64
from speech_recognition import Recognizer,AudioData

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component("streamlit_mic_recorder",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_mic_recorder", path=build_dir)

def mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording",just_once=False,use_container_width=False,format="webm",callback=None,args=(),kwargs={},key=None):
    if not '_last_mic_recorder_audio_id' in st.session_state:
        st.session_state._last_mic_recorder_audio_id=0
    if key and not key+'_output' in st.session_state:
        st.session_state[key+'_output']=None
    new_output=False
    component_value = _component_func(start_prompt=start_prompt,stop_prompt=stop_prompt,use_container_width=use_container_width,format=format,key=key,default=None)
    if component_value is None:
        output=None
    else:
        id=component_value["id"]
        new_output=(id>st.session_state._last_mic_recorder_audio_id)
        if new_output or not just_once:
            audio_bytes=base64.b64decode(component_value["audio_base64"])
            sample_rate=component_value["sample_rate"]
            sample_width=component_value["sample_width"]
            format=component_value["format"]
            output={"bytes":audio_bytes,"sample_rate":sample_rate,"sample_width":sample_width,"format":format,"id":id}
            st.session_state._last_mic_recorder_audio_id=id
        else:
            output=None
    if key:
        st.session_state[key+'_output']=output
    if new_output and callback:
        callback(*args,**kwargs)
    return output
    
def speech_to_text(start_prompt="Start recording",stop_prompt="Stop recording",just_once=False,use_container_width=False,language='en',callback=None,args=(),kwargs={},key=None):
    if not '_last_speech_to_text_transcript_id' in st.session_state:
        st.session_state._last_speech_to_text_transcript_id=0
    if key and not key+'_output' in st.session_state:
        st.session_state[key+'_output']=None
    audio = mic_recorder(start_prompt=start_prompt,stop_prompt=stop_prompt,just_once=just_once,use_container_width=use_container_width,format="wav",key=key)
    new_output=False
    if audio is None:
        output=None
    else:
        id=audio['id']
        new_output=(id>st.session_state._last_speech_to_text_transcript_id)
        if new_output or not just_once:
            st.session_state._last_speech_to_text_transcript_id=id
            r = Recognizer()
            audio_data = AudioData(audio['bytes'],audio['sample_rate'],audio['sample_width'])
            try:
                output = r.recognize_google(audio_data,language=language)
            except:
                output=None
    if key:
        st.session_state[key+'_output']=output
    if new_output and callback:
        callback(*args,**kwargs)
    return output

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
    


    
