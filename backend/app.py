"""Corte Studio Instagram importer. Public single reels only; no credentials."""
import os, re, sys, time, shutil, tempfile, threading, subprocess, logging, uuid
from importlib.metadata import version, PackageNotFoundError
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
logger = logging.getLogger('uvicorn.error')

def downloader_version():
    try: return version('yt-dlp')
    except PackageNotFoundError: return 'not-installed'

def clean_diagnostic(text):
    text=re.sub(r'\x1b\[[0-9;]*m','',str(text or ''))
    text=re.sub(r'https?://[^\s]+','[url]',text)
    text=re.sub(r'(?:/tmp/|[A-Za-z]:\\)[^\s]+','[archivo temporal]',text)
    return ' | '.join(line.strip() for line in text.splitlines() if line.strip())[-2500:]

def downloader_failure(output):
    message=str(output or '').lower()
    # This common upstream message is deliberately ambiguous: do not report it
    # as proof of either private content or a datacenter ban.
    if any(t in message for t in ['requested content is not available, rate-limit reached or login required', 'empty media response']):
        return 'IG_ACCESS_RESTRICTED',502,'Instagram devolvió una respuesta restringida o vacía. Puede ser contenido no disponible, un límite de Instagram o inicio de sesión requerido; esta respuesta no permite distinguirlo.'
    if any(t in message for t in ['too many requests','http error 429','rate-limit','rate limit']):
        return 'IG_RATE_LIMIT',503,'Instagram está limitando las solicitudes del servidor. Espera antes de reintentar; cambiar la URL del editor no resuelve este límite.'
    if any(t in message for t in ['login required','login_required','log in','sign in','private video','private account']):
        return 'IG_LOGIN_REQUIRED',502,'Instagram exige una sesión o restringe el contenido. Este servicio no utiliza cuentas ni cookies; no puede descargar ese reel de forma anónima.'
    if any(t in message for t in ['http error 403','403 forbidden']):
        return 'IG_FORBIDDEN',502,'Instagram rechazó el acceso del descargador (403). El editor sí está conectado; el rechazo ocurre al intentar obtener el video.'
    if any(t in message for t in ['not found','http error 404','has been removed','does not exist']):
        return 'IG_NOT_AVAILABLE',502,'El descargador informa que el contenido no está disponible. Comprueba el enlace original.'
    if 'requested format is not available' in message:
        return 'IG_FORMAT',502,'No se encontró un formato de video compatible. Es un fallo de extracción o formato, no de conexión con el editor.'
    if any(t in message for t in ['unable to extract','unsupported url']):
        return 'IG_EXTRACTOR',502,'El descargador no pudo interpretar la respuesta de Instagram. Puede necesitar una actualización; consulta el diagnóstico de Render.'
    if any(t in message for t in ['timed out','timeout','connection reset','name resolution']):
        return 'IG_NETWORK',504,'Falló la conexión del servidor con Instagram. Espera y vuelve a intentarlo más tarde.'
    return 'IG_DOWNLOAD_ERROR',502,'El descargador falló por una causa no identificada. Consulta en Render la referencia del error para ver la causa técnica.'

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
def health(): return {'status':'ok','service':'corte-instagram','version':2,'downloaderVersion':downloader_version(),'mode':'local' if LOCAL_MODE else 'hosted'}

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
        cmd=[sys.executable,'-m','yt_dlp','--ignore-config','--no-playlist','--no-progress','--socket-timeout','20','--retries','1','--max-filesize',str(MAX_BYTES),'--match-filter','duration <= 300','-f','b[ext=mp4]/b','-o',str(folder/'reel.%(ext)s'),url]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
        if result.returncode:
            error_code,status,explanation=downloader_failure(result.stderr)
            reference=uuid.uuid4().hex[:10]
            logger.warning('Reel failure ref=%s category=%s yt-dlp=%s diagnostic=%s',reference,error_code,downloader_version(),clean_diagnostic(result.stderr or result.stdout))
            raise HTTPException(status,f'{error_code}: {explanation} Referencia: {reference}.')
        files=[p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ('.mp4','.webm','.mov')]
        if len(files)!=1:
            reference=uuid.uuid4().hex[:10]
            logger.warning('Reel no output ref=%s yt-dlp=%s diagnostic=%s',reference,downloader_version(),clean_diagnostic((result.stderr or '')+'\n'+(result.stdout or '')))
            raise HTTPException(422,f'IG_NO_FILE: No se obtuvo un archivo compatible de hasta cinco minutos y 100 MB. Referencia: {reference}.')
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
