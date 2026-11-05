# Corte Studio · Video Corrector

Editor de video en español con interfaz oscura, bordes redondeados, línea de tiempo multipista, textos, audio, filtros, chroma key, fotogramas clave, guardado local y exportación mediante MediaRecorder.

## Abrir el editor

Con GitHub Pages configurado para publicar `main` y la carpeta raíz, la dirección del editor es:

https://alvaroporras2002-coder.github.io/video-corrector/

También puedes abrir `index.html` directamente. El guardado y las APIs multimedia dependen del navegador. Recomendado: Chrome o Edge actualizado en computadora. Los proyectos se guardan en ese navegador; descarga copias para conservarlos.

## Archivos

- `index.html`: aplicación completa; no necesita compilación ni dependencias externas para editar.
- `config.json`: dirección opcional del servidor de Instagram, compartida por la página publicada.
- `backend/`: servicio Python/FastAPI con yt-dlp y Dockerfile.
- `INSTAGRAM.md`: instalación, conexión y límites de descarga.
- `tests/`: comprobaciones del contrato del servidor y del HTML.
- `.github/workflows/checks.yml`: comprobaciones automáticas en GitHub Actions.

## Instagram: estado real

El editor y el código del servidor están incluidos. **Subirlos a GitHub NO pone en marcha el servidor Python.** GitHub Pages solo sirve archivos estáticos. Para que funcione “Descargar e importar”, despliega `backend/` en un servicio Python o Docker con HTTPS y salida a internet.

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
python -m unittest discover -s tests -p 'test_*.py'
```

Las pruebas del backend simulan Instagram: comprueban validación, respuestas, tiempos de espera y limpieza de archivos, sin descargar contenido real. La inspección visual, la sincronización audiovisual y la exportación con códecs reales siguen pendientes de verificación en un navegador; consulta Ayuda en el editor.
