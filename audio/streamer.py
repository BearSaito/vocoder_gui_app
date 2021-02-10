import pyaudio
import wave

class AudioStreamer(object):
    def __init__(self, rate, channel, format, chunks, audio, device_id):
        self.rate = int(rate)
        self.channel = channel
        self.format = format
        self.chunks = chunks
        self.audio = audio
        self.device_id = device_id
        self.is_active = True
        self.reset()
    
    def reset(self):
        self.count = 0
        self.wav = b''

    def start(self):
        def audio_callback(in_data, frame_count, time_info, status):
            self.wav += in_data
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue
        
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channel,
                                      rate=self.rate,
                                      input=True,
                                      output=False,
                                      frames_per_buffer=self.chunks,
                                      stream_callback=audio_callback,
                                      input_device_index=self.device_id)
        self.is_active = False
        self.stream.stop_stream()

    def get_all(self):
        return self.wav

    def stop(self):
        self.stream.stop_stream()
        self.is_active = False

    def restart(self):
        self.is_active = True
        self.reset()
        self.stream.start_stream()

    def write_wav(self, data, path=""):
        with wave.open(path, "wb") as wo:  # 追記
            wo.setnchannels(self.channel)
            wo.setsampwidth(self.audio.get_sample_size(self.format))
            wo.setframerate(self.rate)
            wo.writeframes(data)
    
    def read_wav(self, path):
        self.stop()
        with wave.open(path, "rb") as ro:  # 追記
            data = ro.readframes(ro.getnframes())
        self.wav = data
        return data


class AudioPlaybackLoop:
    def __init__(self, rate, channel=1, chunks=1024, device_id=None):
        self.audio_output = pyaudio.PyAudio()
        self.speaker = self.audio_output.open(format=self.audio_output.get_format_from_width(2),
                                              channels=channel,
                                              rate=int(rate),
                                              input=False,
                                              output=True,
                                              output_device_index=device_id)
        self.data = b''
        self.chunks = chunks
        self.active = False

    def play(self, data):
        self.speaker.write(data)

    def is_play(self):
        return self.active
