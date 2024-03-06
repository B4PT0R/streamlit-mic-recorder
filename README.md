# Streamlit Mic Recorder

Streamlit component that allows to record mono audio from the user's microphone, and/or perform speech recognition
directly.

## Installation instructions

```sh
pip install streamlit-mic-recorder
```

## Usage instructions

Two functions are provided (with the same front-end):

### 1. Mic Recorder

```python
from streamlit_mic_recorder import mic_recorder
audio = mic_recorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    format="webm",
    callback=None,
    args=(),
    kwargs={},
    key=None
)
```

Renders a button. Click to start recording, click to stop. Returns None or a dictionary with the following structure:

```python
{
    "bytes": audio_bytes,  # audio bytes mono signal, can be processed directly by st.audio
    "sample_rate": sample_rate,  # depends on your browser's audio configuration
    "sample_width": sample_width,  # 2
    "format": "webm", # The file format of the audio sample
    "id": id  # A unique timestamp identifier of the audio
}
```

sample_rate and sample_width are provided in case you need them for further audio processing.

Arguments:

- 'start/stop_prompt', the prompts appearing on the button depending on its recording state.
- 'just_once' determines if the widget returns the audio only once just after it has been recorded (and then None), or
  on every rerun of the app. Useful to avoid reprocessing the same audio twice.
- 'use_container_width' just like for st.button, determines if the button fills its container width or not.
- 'format': The desired file format of the audio sample (can be either "webm" or "wav") 
- 'callback': an optional callback being called when a new audio is received
- 'args/kwargs': optional args and kwargs passed to the callback when triggered

Remark:
When using a key for the widget, due to how streamlit's component API works, the associated state variable will only
contain the raw unprocessed output from the React frontend, which was not very practical.
For convenience, I added a special state variable to be able to access the output in the expected format (the dictionary
described above) more easily. If `key` is the key you gave to the widget, you can acces the properly formatted output
via `key+'_output'` in the session state.
Here is an example on how it can be used within a callback:

```python
from streamlit_mic_recorder import mic_recorder
import streamlit as st

def callback():
    if st.session_state.my_recorder_output:
        audio_bytes = st.session_state.my_recorder_output['bytes']
        st.audio(audio_bytes)


mic_recorder(key='my_recorder', callback=callback)
```

### 2. Speech recognition with Google API

```python
from streamlit_mic_recorder import speech_to_text
text = speech_to_text(
    language='en',
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    callback=None,
    args=(),
    kwargs={},
    key=None
)
```

Renders a button. Click to start recording, click to stop. Returns None or a text transcription of the recorded speech
in the chosen language.
Similarly to the mic_recorder function, you can pass a callback that will trigger when a new text transcription is
received, and access this transcription directly in the session state by adding an '_output' suffix to the key you chose
for the widget.

```python
import streamlit as st
from streamlit_mic_recorder import speech_to_text
def callback():
    if st.session_state.my_stt_output:
        st.write(st.session_state.my_stt_output)


speech_to_text(key='my_stt', callback=callback)
```

## Example

```python
import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text

state = st.session_state

if 'text_received' not in state:
    state.text_received = []

c1, c2 = st.columns(2)
with c1:
    st.write("Convert speech to text:")
with c2:
    text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

if text:
    state.text_received.append(text)

for text in state.text_received:
    st.text(text)

st.write("Record your voice, and play the recorded audio:")
audio = mic_recorder(start_prompt="⏺️", stop_prompt="⏹️", key='recorder')

if audio:
    st.audio(audio['bytes'])
```

## Using it with OpenAI Whisper API

For those interested in using the mic recorder component with Whisper here is the script I'm using, working just fine
for me.

```python
# whisper_stt.py

from streamlit_mic_recorder import mic_recorder
import streamlit as st
import io
from openai import OpenAI
import os


def whisper_stt(openai_api_key=None, start_prompt="Start recording", stop_prompt="Stop recording", just_once=False,
               use_container_width=False, language=None, callback=None, args=(), kwargs=None, key=None):
    if not 'openai_client' in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
    if not '_last_speech_to_text_transcript_id' in st.session_state:
        st.session_state._last_speech_to_text_transcript_id = 0
    if not '_last_speech_to_text_transcript' in st.session_state:
        st.session_state._last_speech_to_text_transcript = None
    if key and not key + '_output' in st.session_state:
        st.session_state[key + '_output'] = None
    audio = mic_recorder(start_prompt=start_prompt, stop_prompt=stop_prompt, just_once=just_once,
                         use_container_width=use_container_width,format="webm", key=key)
    new_output = False
    if audio is None:
        output = None
    else:
        id = audio['id']
        new_output = (id > st.session_state._last_speech_to_text_transcript_id)
        if new_output:
            output = None
            st.session_state._last_speech_to_text_transcript_id = id
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = 'audio.webm'
            success = False
            err = 0
            while not success and err < 3:  # Retry up to 3 times in case of OpenAI server error.
                try:
                    transcript = st.session_state.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_bio,
                        language=language
                    )
                except Exception as e:
                    print(str(e))  # log the exception in the terminal
                    err += 1
                else:
                    success = True
                    output = transcript.text
                    st.session_state._last_speech_to_text_transcript = output
        elif not just_once:
            output = st.session_state._last_speech_to_text_transcript
        else:
            output = None

    if key:
        st.session_state[key + '_output'] = output
    if new_output and callback:
        callback(*args, **(kwargs or {}))
    return output
```

Usage:

```python
import streamlit as st
from whisper_stt import whisper_stt

text = whisper_stt(openai_api_key="<your_api_key>", language = 'en')  
# If you don't pass an API key, the function will attempt to retrieve it as an environment variable : 'OPENAI_API_KEY'.
if text:
    st.write(text)
```

## Changelog

- 6 march 2024 : Added the possibility to choose the file format of the audio sample coming from the frontend.
    - "webm" : compressed / low latency / natively supported by most browsers and Whisper API. 
    - "wav" : slower / supported by most STT engines.

    Planning to add support for more audio file formats (mp3, ...)
