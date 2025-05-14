"""
Web Crawler Avanzado
-------------------
Script para realizar crawling recursivo de una web con las siguientes características:
- Procesamiento paralelo mediante ThreadPoolExecutor
- Filtrado de URLs según patrones definidos
- Identificación de tipos de recursos (HTML, PDF, imágenes, etc.)
- Almacenamiento en chunks de resultados en archivos CSV separados
- Control de URLs ya visitadas
"""

import requests
import re
import os
import csv
import time
import pandas as pd
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import warnings

# Suprimir advertencias SSL
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class WebCrawler:
    def __init__(self, url_inicial, profundidad_max=3, tamano_chunk=100, max_workers=10, 
                 timeout=10, claves_url=None, dominios_permitidos=None, patrones_excluir=None):
        """
        Inicializa el crawler con los parámetros configurables.
        
        Args:
            url_inicial: URL desde donde comenzar el crawling
            profundidad_max: Nivel máximo de profundidad para crawlear (default: 3)
            tamano_chunk: Tamaño de los chunks para guardar resultados (default: 100)
            max_workers: Número máximo de hilos paralelos (default: 10)
            timeout: Tiempo máximo de espera para las peticiones HTTP (default: 10)
            claves_url: Lista de patrones para filtrar URLs de interés (default: None = todas)
            dominios_permitidos: Lista de dominios permitidos (default: None = solo el dominio inicial)
            patrones_excluir: Patrones de URL a excluir (default: None)
        """
        self.url_inicial = url_inicial
        self.profundidad_max = profundidad_max
        self.tamano_chunk = tamano_chunk
        self.max_workers = max_workers
        self.timeout = timeout
        self.claves_url = claves_url or []
        self.patrones_excluir = patrones_excluir or []
        self.session = requests.Session()
        
        # Extraer el dominio de la URL inicial si no se especifican dominios permitidos
        if dominios_permitidos:
            self.dominios_permitidos = dominios_permitidos
        else:
            dominio_inicial = urlparse(url_inicial).netloc
            self.dominios_permitidos = [dominio_inicial]
        
        # Estructuras de datos para el seguimiento
        self.urls_visitadas = set()
        self.buffer_paginas = []
        self.buffer_pdfs = []
        self.contador_chunk_paginas = 1
        self.contador_chunk_pdf = 1
        
        # Headers para simular un navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        self.session.headers.update(self.headers)
        
        # Definir patrones para identificar tipos de recursos
        self.patrones_recursos = {
            'pdf': r'\.pdf',
            'imagen': r'\.(jpg|jpeg|png|gif|bmp|svg|webp)',
            'audio': r'\.(mp3|wav|ogg|flac|aac)',
            'video': r'\.(mp4|avi|mov|wmv|flv|mkv|webm)',
            'comprimido': r'\.(zip|rar|7z|tar|gz|bz2)',
        }
    
    def identificar_tipo_recurso(self, url):
        """
        Identifica el tipo de recurso basado en la URL utilizando expresiones regulares.
        
        Args:
            url: URL a analizar
            
        Returns:
            String con el tipo de recurso identificado
        """
        url_lower = url.lower()
        
        for tipo, patron in self.patrones_recursos.items():
            if re.search(patron, url_lower):
                return tipo
                
        # Por defecto, asumimos que es una página HTML
        return "paginas"
    
    def es_url_valida(self, url):
        """
        Verifica si una URL es válida según los criterios de filtrado.
        
        Args:
            url: URL a verificar
            
        Returns:
            Boolean indicando si la URL cumple los criterios para ser procesada
        """
        # Verificar si la URL ya ha sido visitada
        if url in self.urls_visitadas:
            return False
        
        # Verificar si es una URL (no javascript, mailto, tel, etc.)
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Verificar dominio permitido
        dominio = urlparse(url).netloc
        if not any(dominio == d or dominio.endswith('.' + d) for d in self.dominios_permitidos):
            return False
        
        # Verificar patrones de exclusión
        for patron in self.patrones_excluir:
            if re.search(patron, url):
                return False
        
        # Verificar claves de inclusión (si hay alguna especificada)
        if self.claves_url:
            return any(clave in url for clave in self.claves_url)
        
        return True
    
    def guardar_chunk(self, buffer, contador, tipo):
        """
        Guarda un chunk de resultados en un archivo CSV.
        
        Args:
            buffer: Lista de resultados a guardar
            contador: Número de chunk
            tipo: Tipo de contenido ('paginas' o 'pdf')
            
        Returns:
            Contador actualizado
        """
        if not buffer:
            return contador
        
        # Crear DataFrame y guardar como CSV
        df = pd.DataFrame(buffer)
        nombre_archivo = os.path.join("resultados_scraper",f"resultados_crawl_{tipo}_chunk_{contador}_claude.csv")
        
        # Asegurar que tengamos las columnas correctas en el orden adecuado
        columnas = ['url', 'profundidad', 'tipo']
        if 'contenido' in df.columns:
            columnas.append('contenido')
            
        df = df[columnas]
        
        # Guardar como CSV
        df.to_csv(nombre_archivo, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
        
        return contador + 1
    
    def procesar_url(self, url, profundidad):
        """
        Procesa una URL: descarga contenido, extrae enlaces y clasifica resultados.
        
        Args:
            url: URL a procesar
            profundidad: Nivel de profundidad actual
            
        Returns:
            Lista de nuevas URLs encontradas para seguir el crawling
        """
        # Marcar como visitada primero para evitar condiciones de carrera
        self.urls_visitadas.add(url)
        
        tipo_recurso = self.identificar_tipo_recurso(url)
        nuevas_urls = []
        contenido = None
        
        try:
            # Realizar la petición HTTP
            response = self.session.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                verify=False  # Ignorar verificación SSL
            )
            
            # Procesar solo si la respuesta es exitosa (código 200)
            if response.status_code == 200:
                # Si es una página HTML, extraer enlaces y contenido
                if tipo_recurso == "paginas" and 'text/html' in response.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(response.text,"html.parser")
                    
                    # Extraer contenido del body
                    body = soup.find('body')
                    if body:
                        contenido = str(body)
                    
                    # Añadir resultado al buffer de páginas
                    self.buffer_paginas.append({
                        'url': url,
                        'profundidad': profundidad,
                        'tipo': tipo_recurso,
                        'contenido': contenido
                    })
                    
                    # Verificar si necesitamos guardar un chunk
                    if len(self.buffer_paginas) >= self.tamano_chunk:
                        self.contador_chunk_paginas = self.guardar_chunk(
                            self.buffer_paginas, 
                            self.contador_chunk_paginas, 
                            'paginas'
                        )
                        self.buffer_paginas = []
                    
                    # Si no hemos alcanzado la profundidad máxima, seguir extrayendo enlaces
                    if profundidad < self.profundidad_max:
                        # Extraer todos los enlaces
                        for a in soup.find_all('a', href=True):
                            enlace = a['href']
                            
                            # Convertir URLs relativas a absolutas
                            enlace_abs = urljoin(url, enlace)
                            
                            # Normalizar la URL
                            enlace_abs = urllib.parse.unquote(enlace_abs.split('#')[0].split('?')[0])
                            
                            # Si la URL es válida y no ha sido visitada, añadirla a la lista de nuevas URLs
                            if enlace_abs not in self.urls_visitadas and self.es_url_valida(enlace_abs):
                                nuevas_urls.append((enlace_abs, profundidad + 1))
                
                # Si es un PDF
                elif tipo_recurso == "pdf":
                    self.buffer_pdfs.append({
                        'url': url,
                        'profundidad': profundidad,
                        'tipo': tipo_recurso
                    })
                    
                    # Verificar si necesitamos guardar un chunk
                    if len(self.buffer_pdfs) >= self.tamano_chunk:
                        self.contador_chunk_pdf = self.guardar_chunk(
                            self.buffer_pdfs, 
                            self.contador_chunk_pdf, 
                            'pdf'
                        )
                        self.buffer_pdfs = []
                
                # Otros tipos de recursos (imágenes, audio, etc.)
                else:
                    # Simplemente los registramos sin guardarlos en chunks
                    pass
        
        except Exception as e:
            # Manejar errores silenciosamente, opcionalmente se podría implementar
            # un registro de errores para depuración
            pass
        
        return nuevas_urls
    
    def iniciar_crawl(self):
        """
        Inicia el proceso de crawling desde la URL inicial.
        """
        print(f"🕷️ Iniciando crawl desde: {self.url_inicial}")
        print(f"⚙️ Configuración: profundidad={self.profundidad_max}, workers={self.max_workers}, chunk={self.tamano_chunk}")
        
        # Cola de URLs pendientes (url, profundidad)
        cola_urls = [(self.url_inicial, 0)]
        
        # Contador para estadísticas
        urls_procesadas = 0
        
        # Mientras haya URLs en la cola
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            with tqdm(desc="Procesando URLs", unit="url") as pbar:
                while cola_urls:
                    # Obtener lote de URLs para procesar en paralelo
                    lote_actual = cola_urls[:self.max_workers]
                    cola_urls = cola_urls[self.max_workers:]
                    
                    # Evitar procesar URLs ya visitadas
                    lote_filtrado = [(url, prof) for url, prof in lote_actual if url not in self.urls_visitadas]
                    
                    if not lote_filtrado:
                        continue
                    
                    # Procesar URLs en paralelo
                    futures = [executor.submit(self.procesar_url, url, prof) for url, prof in lote_filtrado]
                    
                    # Recoger resultados y actualizar la cola
                    for future in futures:
                        nuevas_urls = future.result()
                        cola_urls.extend(nuevas_urls)
                        urls_procesadas += 1
                        pbar.update(1)
        
        # Guardar los buffers restantes
        if self.buffer_paginas:
            self.guardar_chunk(self.buffer_paginas, self.contador_chunk_paginas, 'paginas')
            
        if self.buffer_pdfs:
            self.guardar_chunk(self.buffer_pdfs, self.contador_chunk_pdf, 'pdf')
        
        print(f"\n✅ Crawl completado. URLs procesadas: {urls_procesadas}")
        print(f"📄 Resultados guardados en archivos CSV:")
        print(f"   - Páginas: resultados_crawl_paginas_chunk_*.csv")
        print(f"   - PDFs: resultados_crawl_pdf_chunk_*.csv")


if __name__ == "__main__":
    # Configuración de ejemplo
    config = {
        'url_inicial': 'https://www.cabildodelanzarote.com/mapa-web/',
        'profundidad_max': 10,
        'tamano_chunk': 500,
        'max_workers': 30,
        'timeout': 75,
        'claves_url': [],  # Dejar vacío para no filtrar por claves
        'dominios_permitidos': ['cabildodelanzarote.com'],  # Dominios permitidos
        'patrones_excluir': [
            r'/wp-admin/',
            r'/login/',
            r'logout',
            r'buscar\?',
            r'mailto',
            r'lanzarotemodaoficial',
            r'calendarsuite',
            r'document_library',
            r'api.whatsapp'
        ]
    }
    
    # Iniciar el crawler
    crawler = WebCrawler(**config)
    crawler.iniciar_crawl()

