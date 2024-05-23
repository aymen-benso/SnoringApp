from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import MeshLinePlot
from kivy.clock import Clock
from kivy_garden.graph import Graph
import pyaudio
import time


class VoiceStream(BoxLayout):
    def __init__(self, **kwargs):
        super(VoiceStream, self).__init__(**kwargs)
        # Graph and PyAudio initialization
        self.graph = Graph(xlabel='Time', ylabel='Amplitude', x_ticks_minor=5,
                           x_ticks_major=25, y_ticks_major=1,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=-0, xmax=25, ymin=-1, ymax=1)
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)

        # Variables for apnea detection
        self.silence_threshold = 0.02  # User-configurable
        self.silence_counter = 0
        self.breath_interval_threshold = 5  # Seconds between breaths (configurable)
        self.last_peak_time = None
        self.apnea_detected = False

        # PyAudio initialization
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, stream_callback=self.callback)
        self.stream.start_stream()

        # Update plot at a fixed interval

    def callback(self, in_data, frame_count, time_info, status):
        gain = 10
        amplitude = max(abs(float(in_data[i*2])/32768) for i in range(1024))  # Calculate maximum amplitude
        self.plot.points = [(i, gain * float(in_data[i*2])/32768) for i in range(1024)]

        # Apnea detection with breath interval
        current_time = time.time()
        if self.last_peak_time is not None and (current_time - self.last_peak_time) > self.breath_interval_threshold:
            self.silence_counter += 1
            if self.silence_counter >= 3:  # Adjust for better accuracy
                self.apnea_detected = True
        else:
            self.silence_counter = 0
            self.last_peak_time = current_time

        return (in_data, pyaudio.paContinue)

    def update_plot(self, dt):
        self.graph.xmin += 1
        self.graph.xmax += 1

        # Trigger alarm if apnea detected with additional checks (e.g., snoring detection)
        if self.apnea_detected:
            # Implement your alarm logic here (sound, notification, etc.)
            print("Possible Apnea detected Triggering alarm...")

class VoiceStreamApp(App):
    def build(self):
        return VoiceStream()

if __name__ == '__main__':
    VoiceStreamApp().run()