import pytest
import numpy as np
from src.audio.capture import AudioCapture

def test_audio_capture_initialization():
    """Test if AudioCapture initializes with default parameters"""
    capture = AudioCapture()
    assert capture.sample_rate == 44100
    assert capture.channels == 1
    assert capture.chunk_size == 1024
    assert capture._stream is None

def test_list_input_devices():
    """Test if we can list audio devices"""
    capture = AudioCapture()
    devices = capture.list_input_devices()
    assert isinstance(devices, list)
    if len(devices) > 0:
        device = devices[0]
        assert 'index' in device
        assert 'name' in device
        assert 'channels' in device
        assert 'sample_rate' in device

@pytest.mark.integration
def test_audio_capture_stream():
    """Test if we can capture audio (requires microphone)"""
    capture = AudioCapture(chunk_size=512)  # Smaller chunk for faster test
    audio_generator = capture.capture_audio()
    
    # Get first audio chunk
    audio_chunk = next(audio_generator)
    
    # Verify the audio data
    assert isinstance(audio_chunk, np.ndarray)
    assert len(audio_chunk) == 512  # Should match chunk_size
    assert audio_chunk.dtype == np.int16 