# prueba_archivo.py 
# Script para dividir un archivo en bloques de 32 bytes y enviarlo por el protocolo 
  
import os 
from emisor import Emisor 

ARCHIVO_ENTRADA = "mensaje_entrada.txt" 
TAMANO_BLOQUE = 32 # Tamaño en bytes de cada trozo/payload 

def enviar_archivo(ruta_archivo: str): 
    if not os.path.exists(ruta_archivo): 
        print(f"❌ El archivo '{ruta_archivo}' no existe. Créalo antes de ejecutar.") 
        return 
    
    # 1. Leer el archivo en modo binario 
    with open(ruta_archivo, "rb") as f: 
        contenido = f.read() 
        
    # 2. Fragmentar el contenido en bloques 
    bloques = [contenido[i:i + TAMANO_BLOQUE] for i in range(0, len(contenido), TAMANO_BLOQUE)] 
    
    print(f"📄 Archivo '{ruta_archivo}' leído ({len(contenido)} bytes). Dividido en {len(bloques)} tramas.") 
    
    # 3. Enviar con el Emisor 
    emisor = Emisor() 
    try: 
        emisor.enviar_mensaje(bloques) 
    finally: 
        emisor.cerrar() 
        
if __name__ == "__main__": 
    enviar_archivo(ARCHIVO_ENTRADA)