import socket
import threading
import logging
import time
from typing import Optional, Callable, Tuple
from .protocol import AudioPacket

class VoIPClient:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """Initialize VoIP client.
        
        Args:
            host: Local host to bind to
            port: Local port to bind to
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        self.sequence_number = 0
        self.running = False
        self.receive_callback: Optional[Callable[[AudioPacket], None]] = None
        
    def start(self, receive_callback: Callable[[AudioPacket], None]):
        """Start the client with a callback for received audio"""
        self.receive_callback = receive_callback
        self.running = True
        
        # Start receive thread
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
    def stop(self):
        """Stop the client"""
        self.running = False
        if hasattr(self, 'receive_thread'):
            self.receive_thread.join()
        self.socket.close()
        
    def send_audio(self, audio_data: bytes, target: Tuple[str, int], 
                  sample_rate: int, channels: int):
        """Send audio data to target address"""
        packet = AudioPacket(
            sequence_number=self.sequence_number,
            timestamp=time.time(),
            audio_data=audio_data,
            sample_rate=sample_rate,
            channels=channels
        )
        
        try:
            self.socket.sendto(packet.to_bytes(), target)
            self.sequence_number += 1
        except Exception as e:
            logging.error(f"Error sending audio: {e}")
            
    def _receive_loop(self):
        """Background thread for receiving audio packets"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65535)  # Max UDP packet size
                packet = AudioPacket.from_bytes(data)
                
                if packet and self.receive_callback:
                    self.receive_callback(packet)
                    
            except Exception as e:
                if self.running:  # Only log if we're still meant to be running
                    logging.error(f"Error receiving audio: {e}") 