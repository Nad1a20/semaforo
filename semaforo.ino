// Semaforo con Arduino UNO
// Rojo (pin 2, 20 s) -> Verde (pin 3, 15 s) -> Amarillo (pin 4, 5 s), en loop.
// Cada segundo envia por Serial el estado y el tiempo restante: "STATE:RED:17"
// El servidor (server.py) lee estas lineas y actualiza la pagina web.

const int PIN_ROJO = 2;
const int PIN_VERDE = 3;
const int PIN_AMARILLO = 4;

const int DUR_ROJO = 20;      // segundos
const int DUR_VERDE = 15;     // segundos
const int DUR_AMARILLO = 5;   // segundos

void setup() {
  pinMode(PIN_ROJO, OUTPUT);
  pinMode(PIN_VERDE, OUTPUT);
  pinMode(PIN_AMARILLO, OUTPUT);
  Serial.begin(9600);
  Serial.println("HELLO:SEMAFORO");
}

// Enciende solo la luz indicada y reporta la cuenta regresiva cada segundo.
void mostrarLuz(int pin, const char *nombre, int duracion) {
  digitalWrite(PIN_ROJO, LOW);
  digitalWrite(PIN_VERDE, LOW);
  digitalWrite(PIN_AMARILLO, LOW);
  digitalWrite(pin, HIGH);
  for (int restante = duracion; restante > 0; restante--) {
    Serial.print("STATE:");
    Serial.print(nombre);
    Serial.print(":");
    Serial.println(restante);
    delay(1000);
  }
}

void loop() {
  mostrarLuz(PIN_ROJO, "RED", DUR_ROJO);
  mostrarLuz(PIN_VERDE, "GREEN", DUR_VERDE);
  mostrarLuz(PIN_AMARILLO, "YELLOW", DUR_AMARILLO);
}
