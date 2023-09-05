import React from 'react';
import { StreamlitComponentBase, Streamlit, withStreamlitConnection } from 'streamlit-component-lib';
import toWav from 'audiobuffer-to-wav';
import './styles.css';

interface State {
    recording: boolean;
}

class MicRecorder extends StreamlitComponentBase<State> {

    private mediaRecorder?: MediaRecorder;
    private audioChunks: Blob[] = [];
    private output?:object;

    public state: State = {
        recording: false
    };

    public componentDidMount(): void {
        super.componentDidMount()
        ///console.log("Component mounted")
    }

    public render(): React.ReactNode {
        //console.log("Component renders");
        const Theme = this.props.theme??{base:'light'};
        const buttonStyle = {
            ...this.props.args["use_container_width"] ? { width: '100%' } : {},
        }
        return (
            <div className="App">
                {this.state.recording ? (
                    <button className="myButton" style={buttonStyle} onClick={this.stopRecording}>{this.props.args["stop_prompt"]}</button>
                ) : (
                    <button className="myButton" style={buttonStyle} onClick={this.startRecording}>{this.props.args["start_prompt"]}</button>
                )}
            </div>
        );
    }

    private startRecording = () => {
        //console.log("Component starts recording");

        navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } }).then(stream => {
            this.mediaRecorder = new MediaRecorder(stream);

            this.mediaRecorder.ondataavailable = event => {
                if (event.data) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onerror = (event) => {
                console.error("MediaRecorder error: ", event);
            };

            this.mediaRecorder.onstop = this.processAndSendRecording;

            this.mediaRecorder.start();

            this.setState({ recording: true });
        }).catch(error => {
            console.error("Error initializing media recording: ", error);
        });
    };

    private stopRecording = async () => {
        if (this.mediaRecorder) {
            //console.log("Component stops recording");
            this.mediaRecorder.stop();
            this.setState({ recording: false });   
        }
    };

    private processRecording = async () => {
        //console.log("Component processing the recording...");
        return new Promise<void>(async (resolve) => {

            const audioBlob = new Blob(this.audioChunks, { type: this.mediaRecorder?.mimeType || 'audio/webm' });

            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
            const sampleRate = audioBuffer.sampleRate;

            const wav: ArrayBuffer = toWav(audioBuffer);

            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result?.toString().split(',')[1];
                const dataToSend = {
                    id:Date.now(),
                    audio_base64: base64String,
                    sample_rate: sampleRate,
                    sample_width: 2
                };
                this.output = dataToSend;
                resolve();
            };
            reader.readAsDataURL(new Blob([wav], { type: 'audio/wav' }));
        });
    };

    private sendDataToStreamlit = () => {
        //console.log("Sending data to streamlit...")
        if (this.output) {
            Streamlit.setComponentValue(this.output);
        }
    };

    private processAndSendRecording = async () => {
        await this.processRecording();
        //console.log("Processing finished")
        this.sendDataToStreamlit();
        //console.log("Data sent to Streamlit")
        
        // Reset class variables
        this.mediaRecorder=undefined
        this.audioChunks = [];
        this.output=undefined
    };
}

export default withStreamlitConnection(MicRecorder);
