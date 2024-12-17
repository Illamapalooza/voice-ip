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
        
        self.audio_capture = AudioCapture()
        self.audio_playback = AudioPlayback()
        self.voip_client = None  # Will be initialized when starting
        
    def start(self):
        """Start the NetVoice application"""
        self.console.print("\n[bold green]Welcome to NetVoice![/]")
        
        # Show local IP addresses
        self.console.print("\n[yellow]Your IP Addresses:[/]")
        for ip in self._get_local_ips():
            self.console.print(f"  {ip}")
        
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
        self.console.print("\n[bold]Network Setup[/]")
        self.console.print("Choose the same port number on both computers")
        port = int(Prompt.ask(
            "Enter port number",
            default="5000"
        ))
        
        mode = Prompt.ask(
            "Are you [1] waiting for connection or [2] connecting to another computer",
            choices=["1", "2"],
            default="1"
        )
        
        if mode == "1":
            self.console.print("[green]Waiting for incoming connection...[/]")
            self.console.print("Share your IP address with the other computer")
            target_host = "0.0.0.0"  # Listen on all interfaces
            local_port = port
            target_port = port
        else:
            target_host = Prompt.ask(
                "Enter the IP address of the computer you want to connect to"
            )
            local_port = port
            target_port = port
            
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

    def _get_local_ips(self):
        """Get all local IP addresses"""
        import socket
        ips = []
        try:
            # Get all network interfaces
            interfaces = socket.getaddrinfo(
                host=socket.gethostname(),
                port=None,
                family=socket.AF_INET
            )
            # Extract unique IP addresses
            ips = list(set(item[4][0] for item in interfaces))
            # Filter out loopback
            ips = [ip for ip in ips if not ip.startswith("127.")]
        except Exception as e:
            logger.error(f"Error getting IP addresses: {e}")
        return ips or ["127.0.0.1"]

def main():
    app = NetVoiceApp()
    app.start()

if __name__ == "__main__":
    main() 