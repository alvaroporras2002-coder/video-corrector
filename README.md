# Corte Studio · Video Corrector

Editor de video en español con interfaz oscura, bordes redondeados, línea de tiempo multipista, textos, audio, filtros, chroma key, fotogramas clave, guardado local y exportación mediante MediaRecorder.

## Sin descargar ni instalar programas

El editor funciona directamente en [GitHub Pages](https://alvaroporras2002-coder.github.io/video-corrector/). Si no puedes instalar nada en tu computadora, activa el backend desde el navegador con la configuración preparada:

[Activar servidor en Render](https://render.com/deploy?repo=https://github.com/alvaroporras2002-coder/video-corrector)

La configuración solicita **un único servicio Free**. Revisa y confirma el despliegue en tu cuenta de Render. Cuando aparezca Live, copia su URL HTTPS en Medios → Instagram → URL base del servicio. Consulta [SIN_INSTALAR.md](SIN_INSTALAR.md).

No necesitas ZIP, Python ni Docker en tu computadora para este modo. El servicio no está activado hasta que lo confirmes en Render. El plan gratuito tiene límites y puede suspenderse; no es ilimitado. Instagram también puede bloquear descargas.

## Uso personal sin pagar alojamiento

Descarga el proyecto completo con **Code → Download ZIP**, extrae la carpeta e instala Python 3.11 o superior. Abre **INICIAR_WINDOWS.bat** en Windows o **INICIAR_MAC.command** en Mac. En Linux ejecuta `sh iniciar_linux.sh`.

El lanzador instala las dependencias la primera vez y abre **http://127.0.0.1:8765/** con el descargador ya conectado. Conserva su ventana abierta. Los reels obtenidos se añaden automáticamente a la línea de tiempo. Consulta [USO_LOCAL.md](USO_LOCAL.md) para el paso a paso y solución de problemas.

No hay cuota mensual de hosting en este modo. Sí necesitas tu computadora e internet; Instagram puede bloquear descargas. Se mantienen los límites de 100 MB y cinco minutos por reel. Este modo solo sirve a tu propia computadora.

## Abrir el editor

Con GitHub Pages configurado para publicar `main` y la carpeta raíz, la dirección del editor es:

https://alvaroporras2002-coder.github.io/video-corrector/

También puedes abrir `index.html` directamente. El guardado y las APIs multimedia dependen del navegador. Recomendado: Chrome o Edge actualizado en computadora. Los proyectos se guardan en ese navegador; descarga copias para conservarlos.

## Archivos

- `index.html`: aplicación completa; no necesita compilación ni dependencias externas para editar.
- `config.json`: dirección opcional del servidor de Instagram, compartida por la página publicada.
- `backend/`: servicio Python/FastAPI con yt-dlp y Dockerfile.
- `iniciar_local.py` y archivos `INICIAR_*`: instalación y arranque local.
- `USO_LOCAL.md`: instrucciones del modo personal sin hosting.
- `INSTAGRAM.md`: instalación, conexión y límites de descarga.
- `tests/`: comprobaciones del contrato del servidor y del HTML.
- `.github/workflows/checks.yml`: comprobaciones automáticas en GitHub Actions.

## Instagram: estado real

El editor y el código del servidor están incluidos. **Subirlos a GitHub NO pone en marcha el servidor Python.** GitHub Pages solo sirve archivos estáticos. Para uso personal utiliza el modo local descrito arriba. Para ofrecerlo a otros clientes desde GitHub Pages, despliega `backend/` en un servicio Python o Docker con HTTPS y salida a internet.

1. Usa `backend` como raíz del servicio y su `Dockerfile`.
2. Configura `ALLOWED_ORIGINS=https://alvaroporras2002-coder.github.io`.
3. Verifica que `https://TU-SERVIDOR/health` responde `status: ok`.
4. En `config.json`, cambia `instagramServiceUrl` por la URL base real. Alternativamente, puedes poner esa URL en el panel Instagram del editor para guardarla solo en tu navegador.
5. Pega el enlace del reel y pulsa Descargar e importar.

No hay un servidor preconfigurado ni se garantiza que el hosting sea gratuito. Instagram puede bloquear descargas incluso de reels públicos. No se solicitan contraseñas ni cookies. Importa contenido propio o autorizado; los videos que ya tengas pueden importarse directamente sin servidor.

El identificador extraído de una URL no confirma por sí solo que el reel exista. El video solo se incorpora después de una respuesta válida y de comprobar que el navegador puede decodificarlo.

## Comprobar el proyecto

Frontend (Node 20 o superior):

```sh
node tests/check-frontend.cjs
```

Backend (Python 3.12):

```sh
pip install -r backend/requirements.txt -r tests/requirements.txt
python iniciar_local.py --check
python -m unittest discover -s tests -p 'test_*.py'
```

Las pruebas del backend simulan Instagram: comprueban validación, respuestas, tiempos de espera y limpieza de archivos, sin descargar contenido real. La inspección visual, la sincronización audiovisual y la exportación con códecs reales siguen pendientes de verificación en un navegador; consulta Ayuda en el editor.
