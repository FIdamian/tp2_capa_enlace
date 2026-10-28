#El proceso que escucha, valida tramas, descarta duplicados y responde ACKs

# receptor.py 
# Módulo Receptor para el protocolo Stop-and-Wait sobre Sockets UDP 
# 
import socket 
from trama import Frame, TIPO_DATOS, TIPO_ACK 
from canal import CanalFisico 

HOST = "127.0.0.1" 
PUERTO_RECEPTOR = 5001 


class Receptor: 
    def __init__(self, host: str = HOST, puerto: int = PUERTO_RECEPTOR, canal: CanalFisico = None): 
        self.host = host 
        self.puerto = puerto 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.socket.bind((self.host, self.puerto)) 
        self.secuencia_esperada = 0 
        self.canal = canal or CanalFisico(proba_corrupcion=0.10, proba_perdida=0.10) 
        self.datos_recibidos = bytearray() 
        
    def iniciar(self): 
        print(f"[RECEPTOR] 🚀 Servidor iniciado. Escuchando en {self.host}:{self.puerto}...\n") 
        try: 
            while True: 
                # 1. Recibir bytes crudos del socket UDP 
                datos_raw, direccion_emisor = self.socket.recvfrom(1024) 
                
                try: 
                    # 2. Intentar desempaquetar la trama (Valida FLAGs y CRC-16) 
                    trama = Frame.desempaquetar(datos_raw) 
                    
                    if trama.tipo == TIPO_DATOS: 
                        # Caso A: Trama correcta y en orden 
                        if trama.num_secuencia == self.secuencia_esperada: 
                            print(f"[RECEPTOR] 🟢 Trama Sec={trama.num_secuencia} recibida OK. Payload: '{trama.payload.decode('utf-8', errors='ignore')}'") 
                            self.datos_recibidos.extend(trama.payload) 
                            
                            # Armar trama ACK 
                            trama_ack = Frame(tipo=TIPO_ACK, num_secuencia=0, num_ack=trama.num_secuencia, payload=b"ACK") 
                            bytes_ack = trama_ack.empaquetar() 
                            
                            # Enviar ACK a través del canal físico ruidoso 
                            bytes_ack_canal = self.canal.transmitir(bytes_ack) 
                            if bytes_ack_canal: 
                                self.socket.sendto(bytes_ack_canal, direccion_emisor) 
                                print(f" └─► ACK {trama.num_secuencia} enviado al emisor.")
                            else: 
                                print(f" └─► ⚠️ ACK {trama.num_secuencia} se perdió en el canal.") 
                                
                            # Alternar secuencia esperada (0 -> 1 -> 0) 
                            self.secuencia_esperada = 1 - self.secuencia_esperada 
                            
                        # Caso B: Trama duplicada 
                        else: 
                            print(f"[RECEPTOR] ⚠️ Trama Sec={trama.num_secuencia} DUPLICADA (esperaba {self.secuencia_esperada}). Reenviando ACK.") 
                            trama_ack = Frame(tipo=TIPO_ACK, num_secuencia=0, num_ack=trama.num_secuencia, payload=b"ACK") 
                            bytes_ack = trama_ack.empaquetar() 
                            bytes_ack_canal = self.canal.transmitir(bytes_ack) 
                            if bytes_ack_canal: 
                                self.socket.sendto(bytes_ack_canal, direccion_emisor) 
                                
                except ValueError as e: 
                    print(f"[RECEPTOR] ❌ Trama descartada -> {e}") 
                    
        except KeyboardInterrupt: 
            print("\n[RECEPTOR] 🛑 Servidor detenido.") 
            print(f"Datos totales acumulados: {self.datos_recibidos.decode('utf-8', errors='ignore')}") 
        finally: 
            self.socket.close() 
            
            
if __name__ == "__main__": 
    receptor = Receptor() 
    receptor.iniciar()