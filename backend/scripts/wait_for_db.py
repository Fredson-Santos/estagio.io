import socket
import time
import sys

def wait_for_postgres(host="db", port=5432, timeout=60):
    start_time = time.time()
    print(f"Aguardando {host}:{port} ficar disponível...", flush=True)
    while True:
        try:
            # Tenta estabelecer uma conexão TCP na porta
            with socket.create_connection((host, port), timeout=1):
                print(f"Conexão bem sucedida com {host}:{port}!", flush=True)
                return True
        except (socket.error, socket.timeout):
            if time.time() - start_time > timeout:
                print(f"Erro: Timeout de {timeout}s aguardando o banco {host}:{port}!", file=sys.stderr, flush=True)
                sys.exit(1)
            time.sleep(1)

if __name__ == "__main__":
    wait_for_postgres()
