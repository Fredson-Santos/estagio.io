import os
import socket
import sys
import time


def wait_for_postgres(host="db", port=5432, timeout=None):
    if timeout is None:
        timeout = int(os.getenv("WAIT_FOR_DB_TIMEOUT", "120"))
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
                print(
                    f"Erro: Timeout de {timeout}s aguardando o banco {host}:{port}!",
                    file=sys.stderr,
                    flush=True,
                )
                sys.exit(1)
            time.sleep(1)


if __name__ == "__main__":
    wait_for_postgres()

