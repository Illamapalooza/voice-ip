import sys
import os
import time
from rich import print
from rich.console import Console

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.audio.capture import AudioCapture

def test_audio_devices():
    """Manual test to list and verify audio devices"""
    console = Console()
    
    try:
        capture = AudioCapture()
        devices = capture.list_input_devices()
        
        console.print("\n[bold green]Available Audio Input Devices:[/]")
        for device in devices:
            console.print(f"\n[yellow]Device {device['index']}:[/]")
            console.print(f"  Name: {device['name']}")
            console.print(f"  Channels: {device['channels']}")
            console.print(f"  Sample Rate: {device['sample_rate']}")
        
        if devices:
            console.print("\n[bold green]Testing audio capture...[/]")
            console.print("Recording for 5 seconds from default device...")
            
            # Test audio capture
            audio_gen = capture.capture_audio()
            start_time = time.time()
            
            while time.time() - start_time < 5:
                chunk = next(audio_gen)
                # Print a simple volume indicator
                volume = abs(chunk).mean()
                bars = "█" * int(volume / 100)
                console.print(f"\rVolume: {bars}", end="")
            
            console.print("\n\n[bold green]Test completed successfully![/]")
            
        else:
            console.print("\n[bold red]No input devices found![/]")
            
    except Exception as e:
        console.print(f"\n[bold red]Error during test:[/] {str(e)}")

if __name__ == "__main__":
    test_audio_devices() 