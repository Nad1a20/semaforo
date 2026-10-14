#!/usr/bin/env python3
"""Servidor sencillo del semaforo.

Lee el puerto serial del Arduino UNO (lineas "STATE:RED:17"), guarda el
ultimo estado y lo expone en /api/status como JSON. Sirve la pagina web
(index.html) que muestra la luz activa y la cuenta regresiva.

Uso:
    python server.py [--port COM4] [--baud 9600] [--demo]
    python server.py --list-ports

Sin Arduino conectado (o con --demo) corre en modo simulado para probar
la pagina. Requiere: pip install pyserial
"""

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

estado = {"light": "NONE", "remaining": 0, "connected": False, "source": "demo"}
candado = threading.Lock()


def detectar_puerto():
    """Busca un Arduino UNO (VID 0x2341) o devuelve el primer puerto serie."""
    try:
        from serial.tools import list_ports
    except ImportError:
        return None
    puertos = list(list_ports.comports())
    for p in puertos:
        if p.vid == 0x2341:  # Arduino SA
            return p.device
    return puertos[0].device if puertos else None


def bucle_serial(puerto, baud):
    """Lee STATE:<LUZ>:<SEGUNDOS> del Arduino y actualiza el estado global."""
    import serial

    ultima = 0.0
    while True:
        try:
            with serial.Serial(puerto, baud, timeout=1) as ser:
                time.sleep(2)  # el Arduino se reinicia al abrir el puerto
                ser.reset_input_buffer()
                with candado:
                    estado["connected"] = True
                    estado["source"] = f"serial:{puerto}"
                print(f"[server] Conectado a {puerto} @ {baud} baud", flush=True)
                while True:
                    linea = ser.readline()  # b'' si no hay datos (timeout)
                    if not linea:
                        # Silencio prolongado: el Arduino no esta enviando.
                        if ultima and time.time() - ultima > 5:
                            with candado:
                                estado["connected"] = False
                        continue
                    try:
                        texto = linea.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        continue
                    if texto.startswith("HELLO"):
                        ultima = time.time()
                        continue
                    if texto.startswith("STATE:"):
                        _, luz, restante = texto.split(":")
                        with candado:
                            estado["light"] = luz
                            estado["remaining"] = int(restante)
                            estado["connected"] = True
                        ultima = time.time()
        except Exception as exc:  # puerto desconectado / no existe
            print(f"[server] Serial no disponible ({exc}); reintentando...", flush=True)
            with candado:
                estado["connected"] = False
            time.sleep(3)


def bucle_demo():
    """Simula el semaforo (20/15/5 s) cuando no hay Arduino."""
    secuencia = [("RED", 20), ("GREEN", 15), ("YELLOW", 5)]
    with candado:
        estado["source"] = "demo"
        estado["connected"] = True
    while True:
        for luz, dur in secuencia:
            for restante in range(dur, 0, -1):
                with candado:
                    estado["light"] = luz
                    estado["remaining"] = restante
                time.sleep(1)


class Manejador(BaseHTTPRequestHandler):
    def _json(self, obj):
        cuerpo = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/api/status":
            with candado:
                self._json(dict(estado))
        elif self.path in ("/", "/index.html"):
            pagina = (BASE_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(pagina)))
            self.end_headers()
            self.wfile.write(pagina)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):  # silencia el log por request
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=None, help="Puerto serial (ej. COM4). Auto si se omite.")
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--demo", action="store_true", help="Simular sin Arduino.")
    ap.add_argument("--http-port", type=int, default=8000)
    ap.add_argument("--list-ports", action="store_true")
    args = ap.parse_args()

    if args.list_ports:
        try:
            from serial.tools import list_ports
            for p in list_ports.comports():
                print(f"{p.device} - {p.description} (VID={p.vid})")
        except ImportError:
            print("pyserial no instalado: pip install pyserial")
        return

    puerto = args.port or detectar_puerto()
    if args.demo or not puerto:
        print("[server] Modo DEMO (sin Arduino).")
        threading.Thread(target=bucle_demo, daemon=True).start()
    else:
        print(f"[server] Usando puerto {puerto}.")
        threading.Thread(target=bucle_serial, args=(puerto, args.baud), daemon=True).start()

    srv = ThreadingHTTPServer(("127.0.0.1", args.http_port), Manejador)
    print(f"[server] Pagina en http://localhost:{args.http_port}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
