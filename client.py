#!/usr/bin/env python3
"""
LAN Chat Room - CLIENT
Run this on every machine (including the host) to join the chat.
You'll be asked for the server's IP address and your username.
"""

import socket
import threading
import sys
import os
import datetime

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

connected = threading.Event()
running   = threading.Event()
running.set()

def clear_line():
    """Overwrite the current input line (so incoming messages don't mess up typing)."""
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def print_incoming(data: str):
    """Print a message received from the server, preserving the input prompt."""
    clear_line()
    sys.stdout.write(data)
    if not data.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.write(f"{C.CYAN}You >{C.RESET} ")
    sys.stdout.flush()

def receive_thread(sock: socket.socket):
    """Background thread: reads messages from server and prints them."""
    while running.is_set():
        try:
            raw = sock.recv(BUFFER)
            if not raw:
                print_incoming(f"\n{C.RED}[Disconnected from server]{C.RESET}\n")
                running.clear()
                break
            text = raw.decode(errors="replace")
            print_incoming(text)
        except (ConnectionResetError, BrokenPipeError, OSError):
            if running.is_set():
                print_incoming(f"\n{C.RED}[Connection lost]{C.RESET}\n")
            running.clear()
            break

def timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    # ── Banner ───────────────────────────────────────────────────────────────
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════╗
║         LAN Chat Room  CLIENT            ║
╚══════════════════════════════════════════╝{C.RESET}
""")

    # ── Get server IP ────────────────────────────────────────────────────────
    try:
        server_ip = input(
            f"  Enter server IP {C.DIM}(ask the host){C.RESET}: "
        ).strip()
        if not server_ip:
            server_ip = "127.0.0.1"
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    # ── Get username ─────────────────────────────────────────────────────────
    try:
        username = input(
            f"  Enter your username {C.DIM}(max 20 chars){C.RESET}: "
        ).strip()[:20]
        if not username:
            username = f"User_{os.getpid() % 1000}"
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    # ── Connect ───────────────────────────────────────────────────────────────
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # low latency

    print(f"\n  {C.DIM}Connecting to {server_ip}:{PORT} ...{C.RESET}")
    try:
        sock.connect((server_ip, PORT))
    except ConnectionRefusedError:
        print(f"  {C.RED}✗ Connection refused. Is the server running?{C.RESET}")
        sys.exit(1)
    except socket.timeout:
        print(f"  {C.RED}✗ Timed out. Check the IP address.{C.RESET}")
        sys.exit(1)
    except OSError as e:
        print(f"  {C.RED}✗ Could not connect: {e}{C.RESET}")
        sys.exit(1)

    print(f"  {C.GREEN}✓ Connected!{C.RESET}\n")

    # Send username as first packet
    sock.sendall(username.encode())

    # Start receiver thread
    t = threading.Thread(target=receive_thread, args=(sock,), daemon=True)
    t.start()

    # ── Main input loop ───────────────────────────────────────────────────────
    try:
        while running.is_set():
            try:
                sys.stdout.write(f"{C.CYAN}You >{C.RESET} ")
                sys.stdout.flush()
                line = input().strip()
            except (EOFError, KeyboardInterrupt):
                line = "/quit"

            if not running.is_set():
                break

            if not line:
                # Clear the prompt we just printed
                sys.stdout.write("\033[A\033[K")
                sys.stdout.flush()
                continue

            if line.lower() == "/quit":
                try:
                    sock.sendall(b"/quit")
                except Exception:
                    pass
                running.clear()
                break

            # Show own message locally with timestamp
            now = timestamp()
            clear_line()
            sys.stdout.write(
                f"{C.DIM}[{now}]{C.RESET} "
                f"{C.MAGENTA}{C.BOLD}You{C.RESET}"
                f"{C.DIM}:{C.RESET} {line}\n"
            )
            sys.stdout.flush()

            try:
                sock.sendall(line.encode())
            except (BrokenPipeError, OSError):
                print(f"{C.RED}[Send failed – disconnected]{C.RESET}")
                running.clear()
                break

    finally:
        running.clear()
        try:
            sock.close()
        except Exception:
            pass
        print(f"\n{C.YELLOW}  Goodbye, {username}!{C.RESET}\n")


if __name__ == "__main__":
    main()
