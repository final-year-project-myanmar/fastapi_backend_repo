import os
import asyncio
from fastapi import WebSocket, WebSocketDisconnect


async def pty_to_ws(master_fd: int, ws: WebSocket):
    """Read bytes from PTY and push to browser."""
    loop = asyncio.get_running_loop()
    try:
        while True:
            # os.read blocks; run it in a thread
            data = await loop.run_in_executor(None, os.read, master_fd, 1024)
            if not data:
                break
            await ws.send_bytes(data)
    except Exception:
        pass
    finally:
        print("WebSocket reader task finished.")
        


async def ws_to_pty(master_fd: int, ws: WebSocket):
    """Read browser messages and write into PTY."""
    try:
        while True:
            msg = await ws.receive()  # dict: may have 'text', 'bytes', or close
            if "text" in msg and msg["text"] is not None:
                text = msg["text"]

                # simple local commands
                if text == "exit":
                    await ws.close()
                    break
                elif text == "clear":
                    # ANSI "RIS" — reset/clear terminal
                    os.write(master_fd, b"\x1bc")
                else:
                    os.write(master_fd, text.encode())

            elif "bytes" in msg and msg["bytes"] is not None:
                os.write(master_fd, msg["bytes"])

            elif msg.get("type") in ("websocket.close", "websocket.disconnect"):
                break

            else:
                # ignore ping/pong/etc.
                pass
    except WebSocketDisconnect:
        pass
    finally:
        print("WebSocket writer task finished.")
