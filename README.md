# ⚡ Vault Studio

> **Fast, Light, and Local Media Streaming Server**

Vault Studio is a lightweight local media engine built in pure Python that converts your device into a local cloud server. It streams videos, plays audio with visualizers, and serves documents across devices on the same Wi-Fi network without heavy external dependencies.

---

## 🔥 Key Features

* **Zero-Dependency Architecture:** Built strictly with Python's native `http.server` module (no Flask, Django, or Node.js required).
* **HTTP 206 Partial Content:** Supports range requests, allowing smooth video seeking, scrubbing, and media streaming without memory bottlenecks.
* **Responsive Dark UI:** Modern glassmorphism dashboard built for mobile accessibility.
* **Dynamic Audio Visualizer:** Animated visualizer bars during audio playback.
* **Cross-Device Wi-Fi Sharing:** Auto-generates a local network IP and QR code for cross-device access.
* **Unified Media Controls:** Integrated top-player frame with continuous playlist playback.

---

## 🚀 How to Run

1. Clone or download this repository.
2. Ensure Python 3 is installed on your device.
3. Place your media files inside the `/sdcard/Download` folder.
4. Execute the server:
   ```bash
   python server.py
  
