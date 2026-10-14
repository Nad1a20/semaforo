# Semáforo — Arduino UNO + servidor + página web

Interfaz web que muestra el status del semáforo conectado al equipo,
con la luz activa y cuenta regresiva al siguiente cambio.
Diseño basado en `Semaforo` (Figma).

## 1. Circuito

| Luz      | Pin Arduino | Duración |
|----------|-------------|----------|
| Roja     | D2          | 20 s     |
| Verde    | D3          | 15 s     |
| Amarilla | D4          | 5 s      |

Cada LED con su resistencia (~220 Ω) a GND. Secuencia en loop:
rojo → verde → amarillo.

## 2. Arduino

1. Abrir `semaforo.ino` en Arduino IDE
   (`C:\Users\nadsa\Desktop\Arduino IDE\Arduino IDE.exe`).
2. Seleccionar placa **Arduino UNO** y el puerto COM correspondiente.
3. Subir el sketch. Abrir el Monitor Serie (9600 baud) para ver
   líneas como `STATE:RED:17`.

## 3. Servidor + página

Requiere Python 3 con `pyserial`:

```powershell
pip install -r requirements.txt
python server.py --list-ports   # ver puertos disponibles
python server.py                # autodetecta el Arduino
python server.py --port COM4    # puerto manual
python server.py --demo         # probar la página sin Arduino
```

Abrir **http://localhost:8000**. El endpoint **/api/status**
devuelve `{"light": "RED", "remaining": 17, ...}` cada 500 ms.

## Protocolo Arduino → servidor

Por Serial (9600 baud), una línea por segundo:

```text
STATE:<RED|GREEN|YELLOW>:<segundos_restantes>
```
