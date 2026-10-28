#Algoritmo de cálculo y verificación de errores (CRC-16 o Checksum)

#Módulo de detección de errores usando CRC-16 (Cyclic Redundancy Check)

def calcular_crc16(datos: bytes) -> int: 
    """Calcula el código CRC-16 (polinomio 0x1021) sobre una secuencia de bytes. Devuelve un entero de 16 bits (0 a 65535)"""
    crc = 0xFFFF
    for byte in datos:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else: 
                crc = (crc << 1) & 0xFFFF
    return crc

def verificar_crc16(datos: bytes, crc_recibido: int) -> bool: 
    """ Verifica si el CRC calculado sobre los datos coincide con el CRC recibido. Devuelve True si los datos están intactos, False si hubo corrupción. """
    return calcular_crc16(datos) == crc_recibido

# Prueba rápida de funcionamiento si se ejecuta este archivo directamente 
if __name__ == "__main__": 
    mensaje = b"Mensaje de prueba de la Capa de Enlace"
    crc = calcular_crc16(mensaje)
    print(f"Mensaje: {mensaje}") 
    print(f"CRC-16 calculado: {crc} (hex: {hex(crc)})")
    print(f"¿Es válido?: {verificar_crc16(mensaje, crc)}")

    # Simular corrupción alterando un byte mensaje_corrupto = b"Mensaje de prueba de la Capa de EnlacX" print(f"¿Mensaje corrupto es válido?: {verificar_crc16(mensaje_corrupto, crc)}")

