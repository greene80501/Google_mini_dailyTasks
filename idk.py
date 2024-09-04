import pychromecast
from gtts import gTTS
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import socket
import time

# Function to read the text from a file
def read_text_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# The path to the text file you want Google Home to read
text_file = "today_events.txt"

# Read the text from the file
text = read_text_from_file(text_file)

# Generate speech using gTTS and save it as an MP3 file
tts = gTTS(text=text, lang='en')
tts_file = "tts_output.mp3"
tts.save(tts_file)

# Start a simple HTTP server to serve the MP3 files
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Starting HTTP server on port 8000...")
    httpd.serve_forever()

# Run the server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Get the local IP address
local_ip = socket.gethostbyname(socket.gethostname())
print(f"Local IP Address: {local_ip}")

# Discover Google Home devices
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Wyatts room speaker"])

if not chromecasts:
    print("No Google Home Mini found.")
else:
    # Select the first found Google Home Mini
    cast = chromecasts[0]
    print(f"Found Chromecast: {cast.name}")
    cast.wait()

    # Play the TTS audio on Google Home Mini
    mc = cast.media_controller
    mc.play_media(f"http://{local_ip}:8000/{tts_file}", "audio/mp3")
    mc.block_until_active()
    print("TTS playback started on Google Home Mini.")

    # Wait for the TTS playback to finish
    while mc.status.player_state == 'PLAYING':
        time.sleep(1)

    # Stop the discovery browser
    browser.stop_discovery()

# Keep the server running
input("Press Enter to stop the server and clean up...")

# Clean up the TTS mp3 file
os.remove(tts_file)
