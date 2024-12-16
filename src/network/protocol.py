from dataclasses import dataclass
from typing import Optional
import struct
import time

@dataclass
class AudioPacket:
    """Audio packet structure for network transmission"""
    sequence_number: int
    timestamp: float
    audio_data: bytes
    sample_rate: int
    channels: int

    HEADER_FORMAT = '!IdII'  # sequence, timestamp, sample_rate, channels
    
    def to_bytes(self) -> bytes:
        """Convert packet to bytes for transmission"""
        header = struct.pack(
            self.HEADER_FORMAT,
            self.sequence_number,
            self.timestamp,
            self.sample_rate,
            self.channels
        )
        return header + self.audio_data

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['AudioPacket']:
        """Create packet from received bytes"""
        header_size = struct.calcsize(cls.HEADER_FORMAT)
        if len(data) < header_size:
            return None
            
        header = struct.unpack(cls.HEADER_FORMAT, data[:header_size])
        audio_data = data[header_size:]
        
        return cls(
            sequence_number=header[0],
            timestamp=header[1],
            sample_rate=header[2],
            channels=header[3],
            audio_data=audio_data
        ) 