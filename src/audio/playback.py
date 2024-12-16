import pyaudio
import numpy as np
import logging
from collections import deque
from threading import Lock
from typing import Optional

class AudioPlayback:
    def __init__(self, sample_rate: int = 44100, channels: int = 1, 
                 chunk_size: int = 1024, buffer_size: int = 10):
        """Initialize audio playback with a jitter buffer.
        
        Args:
            sample_rate: Audio sampling rate in Hz
            channels: Number of audio channels
            chunk_size: Size of audio chunks to play
            buffer_size: Number of chunks to buffer before playing
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        
        self.pyaudio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None
        self.buffer = deque(maxlen=buffer_size)
        self.buffer_lock = Lock()
        
    def start(self):
        """Start audio playback"""
        self._stream = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._callback
        )
        self._stream.start_stream()
        
    def stop(self):
        """Stop audio playback"""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        self.pyaudio.terminate()
        
    def add_audio(self, audio_data: bytes):
        """Add audio data to the playback buffer"""
        with self.buffer_lock:
            self.buffer.append(audio_data)
            
    def _callback(self, in_data, frame_count, time_info, status):
        """Callback for audio playback"""
        try:
            with self.buffer_lock:
                if len(self.buffer) > 0:
                    data = self.buffer.popleft()
                else:
                    # Play silence if buffer is empty
                    data = np.zeros(self.chunk_size, dtype=np.int16).tobytes()
                    
            return (data, pyaudio.paContinue)
            
        except Exception as e:
            logging.error(f"Error in playback callback: {e}")
            return (None, pyaudio.paAbort) 