#El proceso que toma datos, arma tramas, maneja el Timer y retransmite

# emisor.py 
# Módulo Emisor para el protocolo Stop-and-Wait sobre Sockets UDP 
 
import socket 
from trama import Frame, TIPO_DATOS, TIPO_ACK 
from canal import CanalFisico 

HOST = "127.0.0.1" 
PUERTO_RECEPTOR = 5001 
TIMEOUT = 1.5 # Tiempo de espera máximo por el ACK en segundos 

class Emisor: 
    def __init__(self, host: str = HOST, puerto: int = PUERTO_RECEPTOR, canal: CanalFisico = None): 
        self.host = host 
        self.puerto = puerto 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.socket.settimeout(TIMEOUT) # Configurar el temporizador por socket 
        self.num_secuencia = 0 
        self.canal = canal or CanalFisico(proba_corrupcion=0.10, proba_perdida=0.10) 
        
    def enviar_mensaje(self, mensajes: list[bytes]): 
        print(f"[EMISOR] 🚀 Iniciando envío de {len(mensajes)} bloques de datos a {self.host}:{self.puerto}...\n") 
        
        for idx, payload in enumerate(mensajes, 1): 
            ack_recibido = False 
            intentos = 0 
            
            # Bucle Stop-and-Wait: Espera hasta recibir el ACK correcto antes de avanzar al siguiente bloque 
            while not ack_recibido: 
                intentos += 1 
                # 1. Armar la trama de datos 
                trama = Frame( 
                    tipo=TIPO_DATOS, 
                    num_secuencia=self.num_secuencia, 
                    num_ack=0, 
                    payload=payload 
                ) 
                bytes_trama = trama.empaquetar() 
                
                print(f"[EMISOR] 📤 (Bloque {idx}/{len(mensajes)}) Enviando trama Sec={self.num_secuencia} (Intento #{intentos})...") 
                
                # 2. Pasar la trama por el canal físico ruidoso 
                bytes_canal = self.canal.transmitir(bytes_trama) 
                
                if bytes_canal: 
                    self.socket.sendto(bytes_canal, (self.host, self.puerto)) 
                    
                # 3\. Esperar el ACK del receptor con un temporizador (Timeout) 
                try: 
                    datos_ack_raw, _ = self.socket.recvfrom(1024) 
                    trama_ack = Frame.desempaquetar(datos_ack_raw) 
                    
                    if trama_ack.tipo == TIPO_ACK and trama_ack.num_ack == self.num_secuencia: 
                        print(f" └─► 🟢 ACK {trama_ack.num_ack} recibido correctamente. ¡Avance de trama!\n") 
                        ack_recibido = True 
                        # Alternar número de secuencia para el siguiente bloque (0 -> 1 -> 0) 
                        self.num_secuencia = 1 - self.num_secuencia 
                    else: 
                        print(f" └─► ⚠️ ACK inesperado o corrupto. Reenviando trama...\n") 
                        
                except socket.timeout: 
                    print(f" └─► ⏰ TIMEOUT: Venció el tiempo de espera ({TIMEOUT}s) sin recibir ACK. Retransmitiendo...\n") 
                except ValueError as e: 
                    print(f" └─► ❌ Error en ACK recibido ({e}). Retransmitiendo...\n") 
                
        print("[EMISOR] 🏁 Transmisión completada exitosamente.") 
        
    def cerrar(self): 
        self.socket.close() 
        
if __name__ == "__main__": 
    emisor = Emisor() 
    bloques = [ 
        b"Bloque 1: Inicio de la transmision.", 
        b"Bloque 2: Capa de Enlace Stop-and-Wait.", 
        b"Bloque 3: Deteccion de errores con CRC-16.", 
        b"Bloque 4: Enmarcado con Byte Stuffing ~ }.", 
        b"Bloque 5: Fin del mensaje recibido OK." 
    ] 
    
    try: 
        emisor.enviar_mensaje(bloques) 
    finally: 
        emisor.cerrar()