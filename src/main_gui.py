import customtkinter as ctk
import threading
import logging
from typing import Optional
import queue

from audio.capture import AudioCapture
from audio.playback import AudioPlayback
from network.client import VoIPClient

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NetVoiceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.audio_capture = AudioCapture()
        self.audio_playback = AudioPlayback()
        self.voip_client = None
        self.running = False
        self.status_queue = queue.Queue()
        
        # Configure window
        self.title("NetVoice")
        self.geometry("600x700")
        self.grid_columnconfigure(0, weight=1)
        
        self._create_ui()
        self._update_status()
        
    def _create_ui(self):
        """Create the user interface"""
        # Title
        title = ctk.CTkLabel(
            self, 
            text="NetVoice",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, pady=20)
        
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Device selection
        device_label = ctk.CTkLabel(
            main_frame,
            text="Audio Input Device:",
            font=ctk.CTkFont(size=16)
        )
        device_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        devices = self.audio_capture.list_input_devices()
        device_names = [f"{d['index']}: {d['name']}" for d in devices]
        
        self.device_var = ctk.StringVar(value=device_names[0])
        self.device_menu = ctk.CTkOptionMenu(
            main_frame,
            values=device_names,
            variable=self.device_var,
            width=400
        )
        self.device_menu.grid(row=1, column=0, padx=10, pady=(0, 20))
        
        # Network settings
        network_frame = ctk.CTkFrame(main_frame)
        network_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        network_frame.grid_columnconfigure(1, weight=1)
        
        # Port entry
        port_label = ctk.CTkLabel(network_frame, text="Port:")
        port_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.port_entry = ctk.CTkEntry(network_frame)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # IP address entry
        ip_label = ctk.CTkLabel(network_frame, text="Target IP:")
        ip_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.ip_entry = ctk.CTkEntry(network_frame)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Connection mode
        self.mode_var = ctk.StringVar(value="listen")
        
        mode_frame = ctk.CTkFrame(main_frame)
        mode_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        listen_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Listen for connection",
            variable=self.mode_var,
            value="listen",
            command=self._update_mode
        )
        listen_radio.grid(row=0, column=0, padx=20, pady=10)
        
        connect_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Connect to other",
            variable=self.mode_var,
            value="connect",
            command=self._update_mode
        )
        connect_radio.grid(row=0, column=1, padx=20, pady=10)
        
        # Local IP display
        ip_frame = ctk.CTkFrame(main_frame)
        ip_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        ip_title = ctk.CTkLabel(
            ip_frame,
            text="Your IP Addresses:",
            font=ctk.CTkFont(weight="bold")
        )
        ip_title.grid(row=0, column=0, padx=10, pady=5)
        
        ips = self._get_local_ips()
        ip_text = "\n".join(ips)
        ip_list = ctk.CTkLabel(ip_frame, text=ip_text)
        ip_list.grid(row=1, column=0, padx=10, pady=5)
        
        # Start/Stop button
        self.toggle_button = ctk.CTkButton(
            main_frame,
            text="Start",
            command=self._toggle_connection,
            width=200,
            height=40
        )
        self.toggle_button.grid(row=5, column=0, pady=20)
        
        # Status display
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=6, column=0, pady=10)
        
        # Volume meter
        self.volume_meter = ctk.CTkProgressBar(main_frame, width=400)
        self.volume_meter.grid(row=7, column=0, pady=10)
        self.volume_meter.set(0)
        
    def _update_mode(self):
        """Update UI based on selected mode"""
        if self.mode_var.get() == "listen":
            self.ip_entry.configure(state="disabled")
        else:
            self.ip_entry.configure(state="normal")
            
    def _toggle_connection(self):
        """Start or stop the connection"""
        if not self.running:
            self._start_connection()
        else:
            self._stop_connection()
            
    def _start_connection(self):
        """Start the VoIP connection"""
        try:
            # Get settings
            device_index = int(self.device_var.get().split(":")[0])
            port = int(self.port_entry.get())
            
            # Configure network
            if self.mode_var.get() == "listen":
                target_host = "0.0.0.0"
            else:
                target_host = self.ip_entry.get()
                
            # Initialize client
            self.voip_client = VoIPClient(port=port)
            self.target_address = (target_host, port)
            
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
            
            # Update UI
            self.toggle_button.configure(text="Stop")
            self.status_label.configure(text="Connected")
            self._set_controls_state("disabled")
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            
    def _stop_connection(self):
        """Stop the VoIP connection"""
        self.running = False
        if self.voip_client:
            self.voip_client.stop()
        self.audio_playback.stop()
        
        # Update UI
        self.toggle_button.configure(text="Start")
        self.status_label.configure(text="Stopped")
        self._set_controls_state("normal")
        self.volume_meter.set(0)
        
    def _set_controls_state(self, state: str):
        """Enable/disable controls"""
        self.device_menu.configure(state=state)
        self.port_entry.configure(state=state)
        self.ip_entry.configure(state=state)
        
    def _capture_and_send_audio(self, device_index: int):
        """Capture and send audio"""
        try:
            for audio_chunk in self.audio_capture.capture_audio(device_index):
                if not self.running:
                    break
                    
                # Update volume meter
                volume = float(abs(audio_chunk).mean()) / 32768.0
                self.status_queue.put(("volume", volume))
                
                # Send audio
                self.voip_client.send_audio(
                    audio_chunk.tobytes(),
                    self.target_address,
                    self.audio_capture.sample_rate,
                    self.audio_capture.channels
                )
                
        except Exception as e:
            self.status_queue.put(("error", str(e)))
            self.running = False
            
    def _handle_received_audio(self, packet):
        """Handle received audio"""
        try:
            self.audio_playback.add_audio(packet.audio_data)
        except Exception as e:
            self.status_queue.put(("error", str(e)))
            
    def _update_status(self):
        """Update status from queue"""
        try:
            while True:
                msg_type, value = self.status_queue.get_nowait()
                if msg_type == "volume":
                    self.volume_meter.set(value)
                elif msg_type == "error":
                    self.status_label.configure(text=f"Error: {value}")
                    self._stop_connection()
        except queue.Empty:
            pass
            
        self.after(50, self._update_status)
        
    def _get_local_ips(self):
        """Get list of local IP addresses"""
        import socket
        ips = []
        try:
            interfaces = socket.getaddrinfo(
                host=socket.gethostname(),
                port=None,
                family=socket.AF_INET
            )
            ips = list(set(item[4][0] for item in interfaces))
            ips = [ip for ip in ips if not ip.startswith("127.")]
        except Exception as e:
            logging.error(f"Error getting IP addresses: {e}")
        return ips or ["127.0.0.1"]

def main():
    app = NetVoiceGUI()
    app.mainloop()

if __name__ == "__main__":
    main() 