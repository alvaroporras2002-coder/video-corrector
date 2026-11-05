# Corte Studio · Importación de reels

Incluye index.html completo y el servidor real backend/. El servidor alojado NO está desplegado. Para uso personal, abre INICIAR_WINDOWS.bat o INICIAR_MAC.command: el editor local queda conectado automáticamente. Lee USO_LOCAL.md.

## 1. Publicar el editor en GitHub Pages
Sube index.html y .nojekyll a tu repositorio. En Settings → Pages publica la rama y carpeta donde pusiste index.html. No pongas el código Python dentro del HTML: GitHub Pages solo sirve archivos estáticos.

## 2. Desplegar el servidor
Usa un alojamiento que ejecute contenedores Docker o Python (no GitHub Pages). No se incluye ni se promete un plan de hosting gratuito. Configura la carpeta backend como raíz del servicio Docker y su Dockerfile. El proveedor debe ofrecer salida a internet y un tiempo de petición superior a 100 segundos.

Variable de entorno necesaria:
ALLOWED_ORIGINS=https://alvaroporras2002-coder.github.io

El origen NO incluye el nombre del repositorio ni barra final. Si usas otro dominio, sustitúyelo. Para varios orígenes, sepáralos con comas. El proveedor puede definir PORT; por defecto 8000. Publica con HTTPS.

Prueba https://TU-SERVICIO/health: debe devolver status: ok y service: corte-instagram.

Alternativa para desarrollo en tu equipo:
cd backend
python -m venv .venv
Activa el entorno virtual según tu sistema.
pip install -r requirements.txt
Configura ALLOWED_ORIGINS con el origen de tu editor (por ejemplo http://localhost:8000).
uvicorn app:app --host 127.0.0.1 --port 8080
Sirve el HTML en otro puerto. Esta opción necesita mantener tu equipo encendido; GitHub Pages HTTPS normalmente exige un backend HTTPS.

## 3. Conectar y editar
En Medios → Instagram, pega el enlace del reel. En Conexión pega la URL base real del servicio (por ejemplo https://TU-SERVICIO). Pulsa Comprobar conexión y luego Descargar e importar. La URL se recuerda solo en este navegador. El reel descargado aparece en la biblioteca; pulsa su miniatura para añadirlo a la línea de tiempo. También puedes descargar una copia del último reel importado.

## Qué identifica
El editor valida el dominio y extrae el identificador del enlace; esto no verifica por sí solo que el reel exista. Solo una descarga correcta confirma acceso a un archivo de video. Se eliminan parámetros de seguimiento. No se obtiene el título ni el autor mediante datos inventados.

## Límites
Reels públicos de hasta 5 minutos y 100 MB. Instagram puede exigir login o bloquear al servidor incluso con videos públicos. No se solicita tu contraseña, cookies ni sesiones, ni se accede a reels privados. En esos casos importa un archivo que tengas disponible. Utiliza contenido propio o autorizado.

El enlace se envía al servidor que configuras, que contacta con Instagram. El archivo temporal se elimina al terminar la respuesta; el editor conserva el medio como los demás archivos importados. No conectes servicios de origen desconocido. Un CORS restringido no sustituye autenticación: este ejemplo incorpora límite básico de peticiones y concurrencia; para uso público masivo añade autenticación, límites en el proxy y supervisión del almacenamiento. El rate limit es por proceso y se reinicia con el servicio.

Actualiza yt-dlp si Instagram cambia. El Dockerfile instala la versión disponible al construir; reconstruye y valida después de actualizar. La descarga en contenedores usa formatos combinados para no necesitar ffmpeg.

## Pruebas
Se comprobaron sintaxis JavaScript/Python y 15 casos de validación/canonicalización de URLs. El módulo se conecta al importador existente; no se probaron peticiones reales ni el servicio FastAPI en ejecución. No se ha descargado un reel real ni desplegado un backend durante esta entrega. Las pruebas del editor de video previas y sus límites siguen en Ayuda.
