import sys
import logging
from rich.console import Console
from rich.prompt import Prompt
from rich.logging import RichHandler
import threading
import time

from audio.capture import AudioCapture
from audio.playback import AudioPlayback
from network.client import VoIPClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("netvoice")

class NetVoiceApp:
    def __init__(self):
        self.console = Console()
        self.running = False
        
        # Initialize components
        self.audio_capture = AudioCapture()
        self.audio_playback = AudioPlayback()
        self.voip_client = None  # Will be initialized when starting
        
    def start(self):
        """Start the NetVoice application"""
        self.console.print("\n[bold green]Welcome to NetVoice![/]")
        
        # List available audio devices
        devices = self.audio_capture.list_input_devices()
        self.console.print("\n[yellow]Available Input Devices:[/]")
        for device in devices:
            self.console.print(f"  [{device['index']}] {device['name']}")
            
        # Get device selection
        device_index = int(Prompt.ask(
            "\nSelect input device",
            default="0"
        ))
        
        # Get network settings
        local_port = int(Prompt.ask(
            "Enter local port to listen on",
            default="5000"
        ))
        
        target_host = Prompt.ask(
            "Enter target IP address",
            default="127.0.0.1"
        )
        
        target_port = int(Prompt.ask(
            "Enter target port",
            default="5001"
        ))
        
        # Initialize network client
        self.voip_client = VoIPClient(port=local_port)
        self.target_address = (target_host, target_port)
        
        # Start components
        self.running = True
        self.audio_playback.start()
        self.voip_client.start(self._handle_received_audio)
        
        # Start audio capture thread
        self.capture_thread = threading.Thread(
            target=self._capture_and_send_audio,
            args=(device_index,)
        )
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        self.console.print("\n[bold green]NetVoice is running![/]")
        self.console.print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Stop the application"""
        self.console.print("\n[yellow]Stopping NetVoice...[/]")
        self.running = False
        
        # Stop all components
        self.voip_client.stop()
        self.audio_playback.stop()
        
        self.console.print("[bold green]NetVoice stopped successfully![/]")
        
    def _capture_and_send_audio(self, device_index: int):
        """Capture and send audio in a loop"""
        try:
            for audio_chunk in self.audio_capture.capture_audio(device_index):
                if not self.running:
                    break
                    
                # Send audio to target
                self.voip_client.send_audio(
                    audio_chunk.tobytes(),
                    self.target_address,
                    self.audio_capture.sample_rate,
                    self.audio_capture.channels
                )
        except Exception as e:
            logger.error(f"Error in audio capture: {e}")
            self.running = False
            
    def _handle_received_audio(self, packet):
        """Handle received audio packets"""
        try:
            self.audio_playback.add_audio(packet.audio_data)
        except Exception as e:
            logger.error(f"Error handling received audio: {e}")

def main():
    app = NetVoiceApp()
    app.start()

if __name__ == "__main__":
    main() 