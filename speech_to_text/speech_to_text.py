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

RATE = 16000
CHUNK = int(RATE / 10)
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
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self.interface = pyaudio.PyAudio()

        self.srteam = self.interface.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate = self.rate,
            input = True,
            frames_per_buffer = self.chunk,
            stream_callback = self.fill_buffer
        )

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self.srteam.stop_stream()
        self.srteam.close()
        self.closed = True
        self.buff.put(None)
        self.interface.terminate()

    def fill_buffer(self, data, count, time, status):
        self.buff.put(data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self.buff.get()

            if chunk is None:
                return

            data = [chunk]

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


if __name__ == "__main__":
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
        quit_transcript = [False]
        
        while 1:
            transcription(responses, quit_transcript)

            if quit_transcript[0]:
                print("Exit")
                break