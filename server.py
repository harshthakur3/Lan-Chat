#!/usr/bin/env python3
"""
LAN Chat Room - SERVER
Run this on the host machine (the one sharing the hotspot).
Everyone connects to this machine's IP address.
"""

import socket
import threading
import datetime
import sys
import os

# ── Config ──────────────────────────────────────────────────────────────────
PORT = 55000
BUFFER = 4096

# ── ANSI Colors ──────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    DIM     = "\033[2m"
    WHITE   = "\033[97m"

# ── State ────────────────────────────────────────────────────────────────────
clients: dict[socket.socket, str] = {}   # socket → username
lock = threading.Lock()

def timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def log(msg: str):
    print(f"{C.DIM}[{timestamp()}]{C.RESET} {msg}")

def broadcast(message: str, exclude: socket.socket | None = None):
    """Send a message to all connected clients."""
    encoded = message.encode()
    with lock:
        dead = []
        for client in clients:
            if client is exclude:
                continue
            try:
                client.sendall(encoded)
            except Exception:
                dead.append(client)
        for c in dead:
            _remove_client(c)

def _remove_client(client: socket.socket):
    """Remove a client (must be called with lock held or inside lock block)."""
    username = clients.pop(client, "unknown")
    try:
        client.close()
    except Exception:
        pass
    return username

def handle_client(client: socket.socket, addr):
    """Handle one connected client in its own thread."""
    try:
        # First message must be the username
        raw = client.recv(BUFFER)
        if not raw:
            client.close()
            return
        username = raw.decode(errors="replace").strip()[:20] or "Anonymous"

        with lock:
            clients[client] = username

        join_msg = (
            f"\n{C.GREEN}{C.BOLD}┌─ {username} joined the room"
            f"{C.RESET}{C.GREEN} ({'•'.join(str(a) for a in addr)}){C.RESET}\n"
        )
        log(f"{C.GREEN}+ {username}{C.RESET} connected from {addr[0]}")
        broadcast(join_msg, exclude=client)

        # Notify the joining client
        welcome = (
            f"{C.CYAN}{C.BOLD}╔══════════════════════════════════════╗\n"
            f"║      Welcome to LAN Chat Room!       ║\n"
            f"╚══════════════════════════════════════╝{C.RESET}\n"
            f"  You joined as {C.YELLOW}{C.BOLD}{username}{C.RESET}\n"
            f"  Type your message and press Enter.\n"
            f"  Type {C.RED}/quit{C.RESET} to leave.\n"
            f"{C.DIM}────────────────────────────────────────{C.RESET}\n"
        )
        client.sendall(welcome.encode())

        # Main receive loop
        while True:
            raw = client.recv(BUFFER)
            if not raw:
                break
            text = raw.decode(errors="replace").strip()
            if not text:
                continue
            if text.lower() == "/quit":
                break

            now = timestamp()
            # Format: [HH:MM:SS] Username: message
            formatted = (
                f"{C.DIM}[{now}]{C.RESET} "
                f"{C.YELLOW}{C.BOLD}{username}{C.RESET}"
                f"{C.DIM}:{C.RESET} {text}\n"
            )
            log(f"{username}: {text}")
            broadcast(formatted, exclude=client)
            # Echo back to sender (so they see others' format)
            # (sender already sees their own input; we just log server-side)

    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        with lock:
            username = _remove_client(client)
        leave_msg = (
            f"\n{C.RED}└─ {username} left the room{C.RESET}\n"
        )
        log(f"{C.RED}- {username}{C.RESET} disconnected")
        broadcast(leave_msg)


def get_local_ip() -> str:
    """Find this machine's LAN IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))        # doesn't actually send anything
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    host_ip = get_local_ip()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", PORT))
    except OSError as e:
        print(f"{C.RED}Could not bind to port {PORT}: {e}{C.RESET}")
        sys.exit(1)

    server.listen(10)

    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════╗
║         LAN Chat Room  SERVER            ║
╚══════════════════════════════════════════╝{C.RESET}

  {C.GREEN}✓ Server is running!{C.RESET}
  
  Share this with your friends:
    IP   : {C.YELLOW}{C.BOLD}{host_ip}{C.RESET}
    Port : {C.YELLOW}{C.BOLD}{PORT}{C.RESET}

  They run:  {C.CYAN}python client.py{C.RESET}
  Then enter IP: {C.YELLOW}{host_ip}{C.RESET}

{C.DIM}  Press Ctrl+C to stop the server.{C.RESET}
{C.DIM}──────────────────────────────────────────{C.RESET}
""")

    try:
        while True:
            try:
                client_sock, addr = server.accept()
                t = threading.Thread(
                    target=handle_client,
                    args=(client_sock, addr),
                    daemon=True
                )
                t.start()
            except OSError:
                break
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Shutting down server...{C.RESET}")
    finally:
        broadcast(f"\n{C.RED}{C.BOLD}[SERVER] Chat room is closing. Goodbye!{C.RESET}\n")
        with lock:
            for c in list(clients):
                try:
                    c.close()
                except Exception:
                    pass
        server.close()
        print(f"{C.GREEN}Server stopped.{C.RESET}")


if __name__ == "__main__":
    main()
