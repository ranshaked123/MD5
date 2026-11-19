import socket, threading, hashlib

TARGET = "ec9c0f7edcc18a98b1f31853b1813301"
STEP = 500_000
tasks = [(i, min(i + STEP, 10_000_000_000)) for i in range(1_000_000_000, 10_000_000_000, STEP)]
found = None

"""
Handles a single client connection: assigns number ranges (GET), verifies results (FOUND),
and re-queues the range on an invalid answer or disconnect.
"""
def handle(conn, addr):
    global found
    curr = None
    while not found:
        try:
            msg = conn.recv(1024).decode().strip()
        except Exception:
            break
        if not msg: break

        if msg == "GET":
            curr = tasks.pop(0) if tasks else None
            out = f"{curr[0]}:{curr[1]}" if curr else "DONE"
            if curr: print(f"Sent {curr[0]:,}-{curr[1]:,} to {addr[0]} (Left: {len(tasks)})")
            try:
                conn.sendall(out.encode())
            except Exception:
                break
            if not curr: break

        elif msg.startswith("FOUND:"):
            ans = msg.split(":")[1]
            if hashlib.md5(ans.encode()).hexdigest() == TARGET:
                found, curr = ans, None
                print(f"\nSUCCESS Number found: {ans} by {addr[0]}\n")
            else:
                print(f"Wrong number {ans} from {addr[0]}. Re-queueing {curr}")
            break

    if curr and not found: tasks.insert(0, curr)
    conn.close()


srv = socket.socket()
srv.bind(("0.0.0.0", 5555))
srv.listen()
print(f"Server listening on port 5555 Total tasks: {len(tasks)}")
while not found:
    srv.settimeout(1.0)
    try:
        c, addr = srv.accept()
        threading.Thread(target=handle, args=(c, addr), daemon=True).start()
    except socket.timeout:
        pass
