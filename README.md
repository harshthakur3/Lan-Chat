<div align="center">
  <h1>🚀 LAN Chat Room</h1>
  <p><b>A completely offline, high-speed, terminal-based chat client for Local Area Networks.</b></p>
</div>

---

Welcome to **LAN Chat Room**, a lightning-fast, zero-dependency Python chat application. Whether you are on a flight, at a remote hackathon, or just want a secure localized space to chat without relying on an internet connection, this tool is for you.

All you need is a shared Wi-Fi network (or a mobile hotspot) and Python!

## ✨ Features

- **📡 Zero Internet Required:** Connect securely over your Local Area Network (LAN) or a mobile hotspot. 
- **⚡ Real-time Multi-Client Sync:** Thread-safe backend architecture ensures instant message delivery to all clients simultaneously.
- **🎨 Beautiful Terminal UI:** Fully customized with ANSI color codes to cleanly differentiate system alerts, timestamps, self, and other users.
- **🕒 Timestamps:** Every message is cleanly logged with accurate timestamps.
- **🔔 Connect/Disconnect Broadcasts:** Real-time logging signals when your friends join or leave the room.
- **🪶 Ultra Lightweight:** Built with 100% standard Python libraries—absolutely **zero dependencies** to `pip install`!

## 🛠️ Prerequisites

- **Python 3.x** installed.
- All users must be connected to the **same Wi-Fi network** or **Hotspot**.

---

## 🚀 How to Use

### 1️⃣ Start the Server (Host Machine)
One person needs to host the chat room. Run the server script and it will automatically figure out your host IP address. 

```bash
python server.py
```

*The terminal will display an IP address and Port (e.g., `192.168.1.5` and `55000`). Share this IP address with your friends!*

### 2️⃣ Join the Chat (Client Machine)
Anyone wanting to join the chat runs the client script. The host can also run a client script in a separate terminal window to join their own room.

```bash
python client.py
```

You will be prompted to:
1. Enter the **Server IP** (provided by the host).
2. Enter your **Username**.

### 3️⃣ Start Chatting!
Type your messages and press `Enter` to communicate in real-time. 

To leave the room gracefully, either type the exit command or press `Ctrl+C`:
```bash
/quit
```

---

## 💻 Tech Stack Highlights

- **Sockets (`socket`)**: Handles lightweight, low-level TCP/IP network communication.
- **Threading (`threading`)**: Non-blocking I/O operations using parallel daemon threads (allows clients to send and receive messages simultaneously).
- **Graceful Error Handling**: Safe teardown protocols for sudden `BrokenPipeError` or `ConnectionResetError` events if a user drops offline unexpectedly.

<br />

<div align="center">
  <i>Happy Offline Chatting! 💬</i>
</div>
