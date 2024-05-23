from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import MeshLinePlot, Graph
from kivy.clock import Clock
import pyaudio
import numpy as np
import tensorflow as tf 


class VoiceStream(BoxLayout):
    def __init__(self, **kwargs):
        super(VoiceStream, self).__init__(**kwargs)
        # Graph and PyAudio initialization
        self.graph = Graph(xlabel='Time', ylabel='Amplitude', x_ticks_minor=5,
                           x_ticks_major=25, y_ticks_major=1,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=-0, xmax=50, ymin=-1, ymax=1)
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)
        self.model = tf.keras.models.load_model('model.h5')

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                                      rate=44100, input=True,
                                      frames_per_buffer=1024,
                                      stream_callback=self.audio_callback)

    def process_audio_data(self, audio_data):
        # Here you can process your audio data and update your graph
        self.plot.points = [(i, j / 32767.) for i, j in enumerate(audio_data)]
        
        # Reshape audio_data for model prediction
        audio_data = audio_data.reshape(1, -1)
        
        # Use the model to predict if there is snoring
        prediction = self.model.predict(audio_data)
        
        # If prediction is above a certain threshold, print snoring detected
        if prediction[0] > 0.5:

            print("Snoring detected")

    def audio_callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.process_audio_data(audio_data)
        return (in_data, pyaudio.paContinue)

class VoiceStreamApp(App):
    def build(self):
        return VoiceStream()

    def on_stop(self):
        # Close the audio stream properly when the app exits
        self.root.stream.stop_stream()
        self.root.stream.close()
        self.root.audio.terminate()

if __name__ == '__main__':
    VoiceStreamApp().run()
