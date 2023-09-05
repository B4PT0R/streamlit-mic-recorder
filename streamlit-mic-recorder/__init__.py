import os
import json
import streamlit.components.v1 as components
import base64
from speech_recognition import Recognizer,AudioData
_root_=os.path.dirname(os.path.abspath(__file__))

def rootjoin(*args):
    return os.path.join(_root_,*args)

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component("streamlit-mic-recorder",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend-react/build")
    _component_func = components.declare_component("streamlit-mic_recorder", path=build_dir)

if not os.path.exists(rootjoin('data.json')):
    with open(rootjoin('data.json'),'w') as f:
        json.dump({'id':0},f)

def mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording",just_once=True,use_container_width=False,key=None):
    component_value = _component_func(start_prompt=start_prompt,stop_prompt=stop_prompt,use_container_width=use_container_width,key=key,default=None)
    if component_value is None:
        return None
    else:
        with open(rootjoin('data.json'),'r') as f:
            data=json.load(f)
        id=component_value["id"]
        audio_bytes=base64.b64decode(component_value["audio_base64"])
        sample_rate=component_value["sample_rate"]
        sample_width=component_value["sample_width"]
        if id>data['id'] or just_once==False:
            data['id']=id
            with open(rootjoin('data.json'),'w') as f:
                json.dump(data,f)
            return {"bytes":audio_bytes,"sample_rate":sample_rate,"sample_width":sample_width}
        else: 
            return None
    
def speech_to_text(start_prompt="Start recording",stop_prompt="Stop recording",just_once=True,use_container_width=False,language='en',key=None):
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
    #from streamlit-mic-recorder import mic_recorder,speech_to_text
    
    state=st.session_state

    if 'text_received' not in state:
        state.text_received=[]

    if 'audio_received' not in state:
        state.audio_received=[]

    st.button('st.button for style reference')

    st.write("Record your voice, and print STT response.")
    with st.container():
        text=speech_to_text(start_prompt="⏺️",stop_prompt="⏹️",language='fr',use_container_width=True,key='STT')
    
    if text:       
        state.text_received.append(text)

    for text in state.text_received:
        st.text(text)
    
    st.write("Record your voice, and play the recorded audio.")
    audio=mic_recorder(key='recorder')

    if audio:       
        state.audio_received.append(audio)

    for audio in state.audio_received:
        st.audio(audio['bytes'], format="audio/wav")
    


    
