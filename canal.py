#El simulador de medio ruidoso (invierte bits o descarta paquetes de forma aleatoria)

# canal.py 
# Simulador de Canal Físico Ruidoso para la Capa de Enlace 
 
import random 
import time 

class CanalFisico: 
    def __init__(self, proba_corrupcion: float = 0.15, proba_perdida: float = 0.10, retardo_max: float = 0.05): 
        """ 
        :param proba_corrupcion: Probabilidad de alterar un bit en la trama (0.0 a 1.0) 
        :param proba_perdida: Probabilidad de descartar la trama por completo (0.0 a 1.0) 
        :param retardo_max: Retardo máximo simulado en segundos 
        """
        self.proba_corrupcion = proba_corrupcion 
        self.proba_perdida = proba_perdida 
        self.retardo_max = retardo_max 
        
    def transmitir(self, trama_bytes: bytes) -> bytes | None: 
        """ 
        Simula el paso de la trama por el medio físico:
        1. Simula retardo de propagación. 
        2. Determina si la trama se pierde. 
        3. Determina si la trama se corrompió (volteo de bits). 
        Devuelve los bytes procesados o None si la trama se perdió. 
        """ 
        # 1. Simular retardo de canal 
        if self.retardo_max > 0: 
            time.sleep(random.uniform(0, self.retardo_max)) 
            
        # 2. Simular pérdida de trama 
        if random.random() < self.proba_perdida: 
            print(" [CANAL] ❌ ¡PÉRDIRA! La trama se perdió en el medio físico.") 
            return None 
        
        # 3. Simular corrupción de bits 
        if random.random() < self.proba_corrupcion: 
            print(" [CANAL] ⚡ ¡RUIDO! Se corrompió un bit en la trama.") 
            trama_corrupta = bytearray(trama_bytes) 
            # Modificar un bit en una posición aleatoria (evitando tocar el inicio) 
            idx = random.randint(1, len(trama_corrupta) - 2) if len(trama_corrupta) > 2 else 0 
            trama_corrupta[idx] ^= (1 << random.randint(0, 7)) 
            return bytes(trama_corrupta) 
        
        # Si no hubo fallas, la trama pasa intacta 
        print(" [CANAL] 🟢 Trama transmitida sin errores.") 
        return trama_bytes 
    
# Prueba rápida de funcionamiento si se ejecuta este archivo directamente 
if __name__ == "__main__": 
    from trama import Frame, TIPO_DATOS 
    
    print("--- PRUEBA DEL SIMULADOR DE CANAL FÍSICO RUIDOSO ---") 
    canal = CanalFisico(proba_corrupcion=0.30, proba_perdida=0.30, retardo_max=0.01) 
    
    trama = Frame(tipo=TIPO_DATOS, num_secuencia=0, num_ack=0, payload=b"Mensaje de prueba para el canal") 
    bytes_originales = trama.empaquetar() 
    
    print(f"Trama original ({len(bytes_originales)} bytes): {bytes_originales}\n") 
    print("Simulando 10 transmisiones por el canal ruidoso:") 
    
    for i in range(1, 11): 
        print(f"\nIntento #{i}:") 
        resultado = canal.transmitir(bytes_originales) 
        if resultado is None: 
            print(" Receptor: No recibió nada (Provocará Timeout).") 
        else: 
            try: 
                trama_recibida = Frame.desempaquetar(resultado) 
                print(f" Receptor: Trama recibida OK -> Payload: {trama_recibida.payload.decode('utf-8')}") 
            except Exception as e: 
                print(f" Receptor: Error al desempaquetar -> {e}")