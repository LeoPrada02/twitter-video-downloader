
"""
Twitter/X Video Downloader
Descarga videos de Twitter/X usando yt-dlp
"""

import subprocess
import sys
import os
import re
from pathlib import Path


def instalar_ytdlp():
    """Instala yt-dlp si no está disponible."""
    try:
        import yt_dlp
        return True
    except ImportError:
        print("Instalando yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
        print("yt-dlp instalado correctamente.\n")
        return True


def es_url_valida(url: str) -> bool:
    """Verifica si la URL parece ser de Twitter/X."""
    patron = r"https?://(www\.)?(twitter\.com|x\.com)/.+/status/\d+"
    return bool(re.match(patron, url))


def descargar_video(url: str, carpeta_destino: str = ".", calidad: str = "best"):
    """
    Descarga un video de Twitter.
    
    Args:
        url: URL del tweet con video
        carpeta_destino: Carpeta donde guardar el video
        calidad: 'best', 'worst', o resolución específica como '720'
    """
    import yt_dlp

    # Crear carpeta si no existe
    Path(carpeta_destino).mkdir(parents=True, exist_ok=True)

    # Mapear opciones de calidad
    formato = {
        "best": "best",         
        "worst": "worst",
        "720": "best[height<=720]",
        "480": "best[height<=480]",
        "360": "best[height<=360]",
        }.get(calidad, "best")

    opciones = {
        "format": formato,
        "outtmpl": os.path.join(carpeta_destino, "%(uploader)s_%(id)s.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "progress": True,
    }

    print(f"\n Descargando video...")
    print(f"   URL: {url}")
    print(f"   Destino: {os.path.abspath(carpeta_destino)}")
    print(f"   Calidad: {calidad}\n")

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            nombre = ydl.prepare_filename(info)
            print(f"\n✅ Video descargado exitosamente!")
            print(f"   Archivo: {nombre}")
            return nombre
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Error al descargar: {e}")
        print("   Asegúrate de que el tweet sea público y contenga un video.")
        return None
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return None


def obtener_info(url: str):
    """Muestra información del video sin descargarlo."""
    import yt_dlp

    print(f"\n Obteniendo información del video...")

    opciones = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"\n Información del video:")
            print(f"   Título:    {info.get('title', 'N/A')}")
            print(f"   Usuario:   {info.get('uploader', 'N/A')}")
            print(f"   Duración:  {info.get('duration', 'N/A')} segundos")
            print(f"   Fecha:     {info.get('upload_date', 'N/A')}")
            
            formatos = info.get("formats", [])
            resoluciones = set()
            for f in formatos:
                if f.get("height"):
                    resoluciones.add(f["height"])
            if resoluciones:
                print(f"   Calidades: {', '.join(str(r) + 'p' for r in sorted(resoluciones, reverse=True))}")
    except Exception as e:
        print(f"❌ No se pudo obtener información: {e}")


def menu_interactivo():
    """Interfaz interactiva de línea de comandos."""
    print("=" * 55)
    print("        Twitter/X Video Downloader ")
    print("=" * 55)
    print()

    while True:
        print("\n¿Qué deseas hacer?")
        print("  [1] Descargar un video")
        print("  [2] Ver información de un video")
        print("  [3] Descargar varios videos (batch)")
        print("  [0] Salir")
        
        opcion = input("\nOpción: ").strip()

        if opcion == "0":
            print("\n ¡Hasta luego!")
            break

        elif opcion == "1":
            url = input("\nPega la URL del tweet: ").strip()
            if not es_url_valida(url):
                print("  La URL no parece ser de Twitter/X. Intenta de nuevo.")
                continue

            print("\nCalidad: [1] Mejor  [2] 720p  [3] 480p  [4] 360p  [5] Peor")
            cal_opcion = input("Elige calidad (Enter = mejor): ").strip()
            calidades = {"1": "best", "2": "720", "3": "480", "4": "360", "5": "worst"}
            calidad = calidades.get(cal_opcion, "best")

            carpeta = input("Carpeta destino (Enter = carpeta actual): ").strip() or "descargas_twitter"
            descargar_video(url, carpeta, calidad)

        elif opcion == "2":
            url = input("\nPega la URL del tweet: ").strip()
            if not es_url_valida(url):
                print("  La URL no parece ser de Twitter/X.")
                continue
            obtener_info(url)

        elif opcion == "3":
            print("\nIngresa las URLs (una por línea). Escribe 'listo' cuando termines:")
            urls = []
            while True:
                url = input("> ").strip()
                if url.lower() == "listo":
                    break
                if es_url_valida(url):
                    urls.append(url)
                elif url:
                    print("    URL inválida, omitida.")

            if not urls:
                print("No se ingresaron URLs válidas.")
                continue

            carpeta = input("Carpeta destino (Enter = 'descargas_twitter'): ").strip() or "descargas_twitter"
            print(f"\nDescargando {len(urls)} videos...\n")
            for i, url in enumerate(urls, 1):
                print(f"[{i}/{len(urls)}]", end=" ")
                descargar_video(url, carpeta)

        else:
            print("Opción no válida.")


def main():
    """Punto de entrada principal."""
    instalar_ytdlp()

    # Si se pasa una URL como argumento, descargar directamente
    if len(sys.argv) > 1:
        url = sys.argv[1]
        carpeta = sys.argv[2] if len(sys.argv) > 2 else "descargas_twitter"
        calidad = sys.argv[3] if len(sys.argv) > 3 else "best"

        if es_url_valida(url):
            descargar_video(url, carpeta, calidad)
        else:
            print("❌ URL inválida. Uso: python twitter_downloader.py <URL> [carpeta] [calidad]")
    else:
        menu_interactivo()


if __name__ == "__main__":
    main()