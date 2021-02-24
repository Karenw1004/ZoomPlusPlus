# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import pyaudio
from six.moves import queue
from google.cloud import speech
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.realpath('./speech_to_text/key.json')
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10) # 100ms
QUIT = False

class TranscribWindow(QWidget):
    def __init__(self):
        super(TranscribWindow, self).__init__()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.show()
    

class MicStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        # Create a thread-safe buffer of audio data
        self.buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self.audio_interface = pyaudio.PyAudio()

        self.audio_stream = self.audio_interface.open(
            format = pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels = 1, 
            rate = self.rate,
            input = True,
            frames_per_buffer = self.chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback = self.fill_buffer
        )

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self.buff.put(None)
        self.audio_interface.terminate()

    def fill_buffer(self, data, count, time, status):
        self.buff.put(data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self.buff.get()

            if chunk is None:
                return

            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self.buff.get(block = False)

                    if chunk is None:
                        return

                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def transcription(responses, quit_transcript):
    app = QApplication(sys.argv)
    window = TranscribWindow()
    printed = 0

    for response in responses:
        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue
        
        transcript = result.alternatives[0].transcript
        overwrite = " " * (printed - len(transcript))

        if not result.is_final:
            sys.stdout.flush()
            printed = len(transcript)
        else:
            text = transcript + overwrite
            print(text)
            window.label.setText(text)
            printed = 0

            if re.search(r"\b(quit)\b", transcript, re.I):
                quit_transcript[0] = True
            break
    app.exec_()

def listen_print_loop(responses, transcript, q):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    i=0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        q.put(transcript)
        # print(transcript)

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            # sys.stdout.write(transcript + overwrite_chars + "\r")
            # sys.stdout.flush()

            num_chars_printed = len(transcript)

        # else:
            # print(transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.


def transcribe(transcript, q):
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "en-US"
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = RATE,
        language_code = language_code
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config = config,
        interim_results = True
    )

    with MicStream(RATE, CHUNK) as stream:
        generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content = content)
            for content in generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # quit_transcript = [False]
        
        # while 1:
        #     transcription(responses, quit_transcript)

        #     if quit_transcript[0]:
        #         print("Exit")
        #         break

        # Now, put the transcription responses to use.
        listen_print_loop(responses, transcript, q)

if __name__ == "__main__":
    transcribe()
    