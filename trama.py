#define la clase de la trama, serialización de bytes

# trama.py 
# Clase Frame: maneja empaquetado, desempaquetado, serialización y Byte Stuffing. 

from checksum import calcular_crc16, verificar_crc16 

# Bytes especiales para enmarcado (Framing) 
FLAG = 0x7E # Byte delimitador de inicio y fin (carácter '~') 
ESC = 0x7D # Byte de escape (carácter '}') 

# Tipos de trama 
TIPO_DATOS = 0 
TIPO_ACK = 1 
TIPO_NAK = 2 


class Frame: 
    def __init__(self, tipo: int, num_secuencia: int, num_ack: int, payload: bytes = b""): 
        self.tipo = tipo # 0: DATOS, 1: ACK, 2: NAK 
        self.num_secuencia = num_secuencia # 0 o 1 (Stop-and-Wait) 
        self.num_ack = num_ack # 0 o 1 
        self.payload = payload # Datos puros entregados por la Capa de Red 
        
    def empaquetar(self) -> bytes: 
        """ 
        1. Arma el cuerpo (Header + Payload) 
        2. Calcula el CRC-16 sobre el cuerpo y lo adjunta
        3. Aplica Byte Stuffing 
        4. Coloca FLAG al inicio y al final 
        """ 
        longitud = len(self.payload) 
        
        # Header: Tipo (1B), Num_Secuencia (1B), Num_ACK (1B), Longitud Payload (1B) 
        header = bytes([self.tipo, self.num_secuencia, self.num_ack, longitud]) 
        cuerpo = header + self.payload 
        
        # Calcular CRC-16 sobre el cuerpo (2 bytes) 
        crc = calcular_crc16(cuerpo) 
        crc_bytes = crc.to_bytes(2, byteorder='big') 
        
        # Trama completa sin stuffing ni flags 
        trama_raw = cuerpo + crc_bytes 
        
        # Aplicar Byte Stuffing 
        trama_stuffed = bytearray() 
        for byte in trama_raw: 
            if byte == FLAG or byte == ESC: 
                trama_stuffed.append(ESC) # Insertar byte ESC de escape 
            trama_stuffed.append(byte) 
            
        # Enmarcado final: FLAG + Trama_Stuffed + FLAG 
        trama_final = bytes([FLAG]) + bytes(trama_stuffed) + bytes([FLAG]) 
        return trama_final 
    
    @staticmethod 
    def desempaquetar(trama_bytes: bytes) -> 'Frame': 
        """ 
        1. Valida los delimitadores FLAG de inicio y fin 
        2. Remueve el Byte Stuffing 
        3. Separa el cuerpo del CRC-16 y valida el CRC 
        4. Reconstruye el objeto Frame 
        """ 
        if len(trama_bytes) < 8: 
            raise ValueError("Trama demasiado corta para ser válida.") 
        
        if trama_bytes[0] != FLAG or trama_bytes[-1] != FLAG: 
            raise ValueError("Error de enmarcado: no contiene FLAGs de inicio o fin válidos.") 
        
        # Quitar los FLAGs de inicio y fin 
        contenido = trama_bytes[1:-1] 
        
        # Remover Byte Stuffing 
        unstuffed = bytearray() 
        i = 0 
        while i < len(contenido): 
            if contenido[i] == ESC: 
                i += 1 # Saltear el ESC y tomar el byte siguiente como dato literal 
                if i >= len(contenido): 
                    raise ValueError("Error de stuffing: byte ESC al final de la trama.") 
            unstuffed.append(contenido[i]) 
            i += 1 
            
        unstuffed_bytes = bytes(unstuffed) 
        
        # Separar cuerpo y CRC (los últimos 2 bytes son el CRC) 
        cuerpo = unstuffed_bytes[:-2] 
        crc_recibido = int.from_bytes(unstuffed_bytes[-2:], byteorder='big') 
        
        # Validar CRC 
        if not verificar_crc16(cuerpo, crc_recibido): 
            raise ValueError("Error de integridad: CRC no coincide (trama corrupta).") 
        
        # Parsear Header con los índices correspondientes 
        tipo = cuerpo[0] 
        num_secuencia = cuerpo[1] 
        num_ack = cuerpo[2] 
        longitud = cuerpo[3] 
        payload = cuerpo[4:4 + longitud] 
        
        return Frame(tipo, num_secuencia, num_ack, payload) 
    
# Prueba rápida de funcionamiento si se ejecuta este archivo directamente 
if __name__ == "__main__": 
    print("--- PRUEBA DE ARMA Y DESARMA DE TRAMA ---") 
    mensaje_original = b"Hola Mundo ~ } con bytes especiales" 
    trama_envio = Frame(tipo=TIPO_DATOS, num_secuencia=0, num_ack=0, payload=mensaje_original) 
        
    bytes_para_socket = trama_envio.empaquetar() 
    print(f"Bytes serializados para enviar por socket:\n{bytes_para_socket}\n") 
        
    trama_recibida = Frame.desempaquetar(bytes_para_socket) 
    print(f"Tipo: {trama_recibida.tipo}") 
    print(f"Secuencia: {trama_recibida.num_secuencia}") 
    print(f"Payload recuperado: {trama_recibida.payload.decode('utf-8')}") 
    print("\n¡Prueba de enmarcado y CRC exitosa!")