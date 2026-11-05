#!/usr/bin/env python3
"""Start the complete editor and downloader on loopback, without a hosting service."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent
ENV_DIR = ROOT / '.venv-local'

def environment_python():
    return ENV_DIR / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')

def install_dependencies(update=False):
    python = environment_python()
    if not python.is_file():
        print('Preparando el entorno local (solo la primera vez)...', flush=True)
        venv.EnvBuilder(with_pip=True).create(ENV_DIR)
    requirements = ROOT / 'backend' / 'requirements.txt'
    fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = ENV_DIR / '.corte-requirements'
    if not marker.exists() or marker.read_text().strip() != fingerprint or update:
        print('Instalando el descargador y sus dependencias desde PyPI. Necesitas internet...', flush=True)
        command = [str(python), '-m', 'pip', 'install']
        if update:
            command.append('--upgrade')
        subprocess.run(command + ['-r', str(requirements)], check=True)
        marker.write_text(fingerprint)
    subprocess.run([str(python), '-c', 'import fastapi, uvicorn, yt_dlp'], check=True)
    return python

def probe(url):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url + 'health', timeout=2) as response:
            info = json.load(response)
        return info.get('service') == 'corte-instagram' and info.get('mode') == 'local'
    except (OSError, ValueError, urllib.error.URLError):
        return False

def wait_and_open(url, process, launch_browser):
    for _ in range(100):
        if process.poll() is not None:
            return
        if probe(url):
            print('\nEditor listo: ' + url, flush=True)
            print('Pega el reel en Medios > Instagram. La conexion local ya esta configurada.', flush=True)
            if launch_browser:
                webbrowser.open(url)
            return
        time.sleep(.2)
    print('El inicio tarda mas de lo esperado. Revisa los mensajes de esta ventana.', flush=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Corte Studio en tu computadora')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--update', action='store_true', help='Actualizar dependencias y yt-dlp')
    parser.add_argument('--check', action='store_true', help='Preparar dependencias y comprobar instalacion sin abrir el editor')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        parser.error('Instala Python 3.11 o superior (recomendado 3.12 o superior).')
    if not 1024 <= args.port <= 65535:
        parser.error('El puerto debe estar entre 1024 y 65535.')
    if not (ROOT / 'index.html').is_file():
        parser.error('Extrae el ZIP completo. index.html debe estar junto a este archivo.')
    python = install_dependencies(args.update)
    if args.check:
        print('Instalacion local comprobada. Ejecuta otra vez sin --check para abrir el editor.')
        return 0
    url = 'http://127.0.0.1:' + str(args.port) + '/'
    with socket.socket() as check:
        try:
            check.bind(('127.0.0.1', args.port))
        except OSError:
            if probe(url):
                print('Corte Studio ya esta abierto: ' + url)
                if not args.no_browser:
                    webbrowser.open(url)
                return 0
            parser.error('El puerto esta ocupado. Cierra el otro programa o usa --port 8766.')
    environment = os.environ.copy()
    environment['CORTE_LOCAL'] = '1'
    environment['ALLOWED_ORIGINS'] = f'http://127.0.0.1:{args.port},http://localhost:{args.port}'
    print('\nCorte Studio local. Conserva esta ventana abierta; Ctrl+C detiene el servidor.', flush=True)
    process = subprocess.Popen([str(python), '-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', str(args.port)], cwd=ROOT, env=environment)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda *_: process.terminate() if process.poll() is None else None)
    opener = threading.Thread(target=wait_and_open, args=(url, process, not args.no_browser), daemon=True)
    opener.start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        print('\nDeteniendo Corte Studio...', flush=True)
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (subprocess.CalledProcessError, OSError) as error:
        print('\nNo se pudo iniciar: ' + str(error), file=sys.stderr)
        print('Comprueba tu conexion, Python y que la carpeta tenga permiso de escritura.', file=sys.stderr)
        raise SystemExit(1)
