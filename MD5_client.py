import socket, hashlib, multiprocessing, os

SERVER_IP = "127.0.0.1"
TARGET = "ec9c0f7edcc18a98b1f31853b1813301"


"""
Connects a single worker process to the server, requests number ranges (GET),
and searches them for a matching MD5 hash until found or tasks end.
"""
def worker(core_id):
    try:
        s = socket.create_connection((SERVER_IP, 5555), timeout=10)
    except Exception as e:
        print(f"[Core {core_id}] Connection failed: {e}")
        return

    while True:
        try:
            s.sendall(b"GET")
            data = s.recv(1024).decode()
        except Exception as e:
            print(f"[Core {core_id}] Network error: {e}")
            break

        if data == "DONE" or not data:
            print(f"[Core {core_id}] Done.")
            break

        parts = data.split(":")
        start, end = int(parts[0]), int(parts[1])
        print(f"[Core {core_id}] Checking {start:,} - {end:,}")

        for num in range(start, end):
            if hashlib.md5(str(num).encode()).hexdigest() == TARGET:
                print(f"[Core {core_id}] MATCH FOUND: {num}!")
                try: s.sendall(f"FOUND:{num}".encode())
                except Exception: pass
                s.close()
                return
    s.close()

if __name__ == "__main__":
    cores = os.cpu_count()
    print(f"[*] Starting {cores} worker processes...")
    procs = [multiprocessing.Process(target=worker, args=(i,)) for i in range(cores)]
    for p in procs: p.start()
    for p in procs: p.join()
