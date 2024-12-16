import pyaudio
import numpy as np
import logging
from typing import Generator, List, Dict

class AudioCapture:
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 1024):
        """Initialize audio capture with specified parameters.
        
        Args:
            sample_rate (int): Audio sampling rate in Hz
            channels (int): Number of audio channels (1 for mono, 2 for stereo)
            chunk_size (int): Number of frames per buffer
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.pyaudio = pyaudio.PyAudio()
        self._stream = None

    def list_input_devices(self) -> List[Dict[str, any]]:
        """List available audio input devices.
        
        Returns:
            List of dictionaries containing device information
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            dev = self.pyaudio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                devices.append({
                    'index': dev['index'],
                    'name': dev['name'],
                    'channels': dev['maxInputChannels'],
                    'sample_rate': int(dev['defaultSampleRate'])
                })
        return devices

    def capture_audio(self, device_index: int = None) -> Generator[np.ndarray, None, None]:
        """Capture audio stream from selected device.
        
        Args:
            device_index (int, optional): Index of input device to use
            
        Yields:
            numpy.ndarray: Audio chunk as numpy array
        """
        try:
            self._stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )

            while True:
                try:
                    audio_chunk = self._stream.read(self.chunk_size)
                    yield np.frombuffer(audio_chunk, dtype=np.int16)
                except IOError as e:
                    logging.error(f"Error reading from audio stream: {e}")
                    continue

        except Exception as e:
            logging.error(f"Error initializing audio capture: {e}")
            raise

    def __del__(self):
        """Cleanup resources on deletion."""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self.pyaudio:
            self.pyaudio.terminate() 