"""Corte Studio Instagram importer. Public single reels only; no credentials."""
import os, re, sys, time, shutil, tempfile, threading, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from collections import defaultdict, deque
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field

LOCAL_MODE = os.getenv('CORTE_LOCAL') == '1'
app = FastAPI(title='Corte Studio Reel Importer', version='1.1')
if LOCAL_MODE:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1','localhost'])
origins = [x.strip() for x in os.getenv('ALLOWED_ORIGINS','http://localhost:8000,http://127.0.0.1:8000').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET','POST'], allow_headers=['Content-Type'], expose_headers=['Content-Disposition','X-Reel-Code'])
slots = threading.BoundedSemaphore(2)
rate_lock = threading.Lock()
hits = defaultdict(deque)
MAX_BYTES = 100 * 1024 * 1024
class Reel(BaseModel):
    url: str = Field(min_length=10,max_length=2048)

def canonical(raw):
    try:
        u=urlsplit(raw.strip())
        if u.scheme!='https' or u.hostname not in ('instagram.com','www.instagram.com','m.instagram.com') or u.username or u.password or u.port not in (None,443):
            raise ValueError()
        m=re.fullmatch(r'/(?:reel|reels)/([A-Za-z0-9_-]{5,100})/?',u.path)
        if not m: raise ValueError()
        return 'https://www.instagram.com/reel/'+m[1]+'/',m[1]
    except (ValueError,TypeError):
        raise HTTPException(422,'Pega un enlace HTTPS de Instagram con formato /reel/IDENTIFICADOR/.')

@app.get('/health')
def health(): return {'status':'ok','service':'corte-instagram','version':1,'mode':'local' if LOCAL_MODE else 'hosted'}

@app.get('/')
def editor():
    if not LOCAL_MODE: raise HTTPException(404,'Editor disponible en GitHub Pages.')
    path=Path(__file__).resolve().parents[1]/'index.html'
    if not path.is_file(): raise HTTPException(404,'Falta index.html. Extrae el proyecto completo.')
    return FileResponse(path,media_type='text/html',headers={'Cache-Control':'no-store'})

@app.get('/config.json')
def local_config(request: Request):
    if not LOCAL_MODE: raise HTTPException(404,'Configuracion local no disponible.')
    return {'instagramServiceUrl':str(request.base_url).rstrip('/'),'mode':'local'}

@app.post('/api/instagram')
def download(body: Reel, request: Request):
    url,code=canonical(body.url)
    origin=request.headers.get('origin')
    if origin and origin not in origins: raise HTTPException(403,'Este dominio no está autorizado en ALLOWED_ORIGINS.')
    now=time.monotonic();ip=request.client.host if request.client else 'unknown'
    with rate_lock:
        # Remove expired clients to keep this in-process limiter bounded.
        for key in list(hits):
            while hits[key] and now-hits[key][0]>600: hits[key].popleft()
            if not hits[key]: del hits[key]
        q=hits[ip]
        if not LOCAL_MODE and len(q)>=6: raise HTTPException(429,'Límite de seis intentos cada diez minutos. Inténtalo después.')
        if not LOCAL_MODE: q.append(now)
    if not slots.acquire(blocking=False): raise HTTPException(503,'El servidor está ocupado. Inténtalo de nuevo en unos segundos.')
    folder=Path(tempfile.mkdtemp(prefix='corte-reel-'))
    try:
        cmd=[sys.executable,'-m','yt_dlp','--ignore-config','--no-playlist','--no-progress','--no-warnings','--socket-timeout','20','--retries','1','--max-filesize',str(MAX_BYTES),'--match-filter','duration <= 300','-f','b[ext=mp4]/b','-o',str(folder/'reel.%(ext)s'),url]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
        if result.returncode:
            raise HTTPException(502,'Instagram no permitió descargar este reel. Puede requerir iniciar sesión, no ser público o estar bloqueado. No se usan cookies ni contraseñas. Puedes importar el archivo manualmente.')
        files=[p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ('.mp4','.webm','.mov')]
        if len(files)!=1: raise HTTPException(422,'No se obtuvo un video compatible de hasta cinco minutos y 100 MB.')
        path=files[0]
        if not 0<path.stat().st_size<=MAX_BYTES: raise HTTPException(413,'El reel supera el límite de 100 MB.')
        mime={'.mp4':'video/mp4','.webm':'video/webm','.mov':'video/quicktime'}[path.suffix.lower()]
        return FileResponse(path,media_type=mime,filename=f'Instagram-{code}{path.suffix}',headers={'X-Reel-Code':code,'Cache-Control':'no-store'},background=BackgroundTask(shutil.rmtree,folder,ignore_errors=True))
    except subprocess.TimeoutExpired:
        shutil.rmtree(folder,ignore_errors=True)
        raise HTTPException(504,'Instagram tardó demasiado en responder. Prueba más tarde o importa el archivo manualmente.')
    except Exception:
        shutil.rmtree(folder,ignore_errors=True)
        raise
    finally: slots.release()
