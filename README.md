# streamlit-mic-recorder

Streamlit component that allows to record mono audio from the user's microphone, and/or perform speech recognition directly.

## Installation instructions

```sh
$ pip install streamlit-mic-recorder
```

## Usage instructions

Two functions are provided (with the same front-end):

1.
```python
audio=mic_recorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording", 
    just_once=True,
    use_container_width=False,
    key=None
)
```
Renders a button. Click to start recording, click to stop. Returns None or a dictionary with the following structure:
```python
{
    "bytes":audio_bytes, # wav audio bytes mono signal, can be processed directly by st.audio
    "sample_rate":sample_rate, # depends on your browser's audio configuration
    "sample_width":sample_width # 2
}
```
sample_rate and sampe_width are provided in case you need them for audio processing.

Arguments:
- start/stop_prompt, the prompts appearing on the button depending on its recording state.
- 'just_once' determines if the widget returns the audio only once just after it has been recorded (and then None), or on every rerun of the app. Useful to avoid reprocessing the same audio twice.
- 'use_container_width' just like for st.button, determines if the button fills its container width or not.  

2.
```python
text=speech_to_text(
    language='en',
    start_prompt="Start recording",
    stop_prompt="Stop recording", 
    just_once=True,
    use_container_width=False,
    key=None
)
```
Renders a button. Click to start recording, click to stop. Returns None or or a text transcription of the recorded speech in the chosen language. 

## Example

```python
import streamlit as st
from streamlit-mic-recorder import mic_recorder,speech_to_text

state=st.session_state

if 'text_received' not in state:
    state.text_received=[]

if 'audio_received' not in state:
    state.audio_received=[]

st.write("Record your voice, and print STT response.")
with st.container():
    text=speech_to_text(language='fr',use_container_width=True,key='STT')

if text:       
    state.text_received.append(text)

for text in state.text_received:
    st.text(text)

st.write("Record sound, and play the recorded audio.")
audio=mic_recorder(start_prompt="⏺️",stop_prompt="⏹️",key='recorder')

if audio:       
    state.audio_received.append(audio)

for audio in state.audio_received:
    st.audio(audio['bytes'])
```