# Corte Studio en tu computadora

## Primera vez

1. Instala Python 3.11 o superior (recomendado 3.12+) desde https://www.python.org/downloads/. En Windows, marca **Add Python to PATH** durante la instalación.
2. Descarga el repositorio completo desde GitHub: botón **Code → Download ZIP**. También puedes usar el ZIP de la entrega local.
3. **Extrae todo el ZIP** a una carpeta que puedas modificar. No ejecutes los archivos dentro del ZIP.
4. Abre `INICIAR_WINDOWS.bat` (Windows), `INICIAR_MAC.command` (Mac) o ejecuta `sh iniciar_linux.sh` (Linux).
5. La primera vez se crea `.venv-local` y se instalan FastAPI, Uvicorn y yt-dlp desde PyPI. Necesitas internet y espacio en tu computadora. Las siguientes veces se reutiliza la instalación.
6. Se abrirá el editor en `http://127.0.0.1:8765/`. Conserva la ventana de inicio abierta.

Si Mac no permite abrir el archivo `.command`, abre Terminal en la carpeta y ejecuta `python3 iniciar_local.py`. En Linux, instala el componente venv de tu distribución si Python informa que falta.

## Descargar y editar

1. Crea un proyecto.
2. En **Medios → Instagram**, pega la URL de un reel público.
3. Pulsa **Descargar e importar**.
4. Si Instagram permite obtener el archivo, se importa a la biblioteca y se añade al cabezal actual de la línea de tiempo.
5. Edita y exporta tu video como de costumbre.

La conexión viene configurada automáticamente cuando abres el editor desde la dirección local. No necesitas Render, Oracle, Docker, un dominio ni una cuenta de hosting. Para este modo abre la dirección LOCAL; la página de GitHub Pages sigue siendo una instalación separada.

## Cuando termines

Guarda el proyecto y descarga una copia de seguridad. Luego pulsa Ctrl+C en la ventana del servidor. Mientras el servidor esté detenido no se descargan nuevos reels, pero los proyectos guardados permanecen en ese navegador y origen.

## Límites reales

No hay cuota mensual de alojamiento ni límite de seis intentos del modo alojado. Sí se mantienen dos descargas simultáneas, hasta 100 MB y cinco minutos por reel. Necesitas tu conexión a internet y la computadora encendida. Instagram puede bloquear descargas o pedir login; no se usan contraseñas ni cookies y no se promete acceso a cualquier reel. Usa contenido propio o autorizado.

El servidor escucha solo en `127.0.0.1`: es para esta computadora, no para otros clientes por internet. El editor y la descarga comparten origen local, evitando depender de una conexión entre GitHub Pages y un servidor privado.

## Actualizar y resolver problemas

- Si Instagram cambia, cierra el editor local y ejecuta `python iniciar_local.py --update` (Windows) o `python3 iniciar_local.py --update` (Mac/Linux). Actualiza dependencias desde PyPI y vuelve a abrir el editor.
- Puerto ocupado: cierra otra instancia o ejecuta `python iniciar_local.py --port 8766`. Cambiar el puerto cambia el origen del navegador: los proyectos del puerto anterior no aparecerán automáticamente. Exporta e importa una copia de tu proyecto.
- Si el navegador no abre, visita manualmente `http://127.0.0.1:8765/`.
- Error instalando: comprueba Python 3.11+, internet y permisos de escritura. Los detalles aparecen en la consola.
- Si no descarga un reel concreto, importa un archivo que ya tengas. No se simula una descarga exitosa.

## Verificación

Las comprobaciones automatizadas incluyen configuración local, servir el editor, rechazo de dominios ajenos, bloqueo de archivos fuente, ausencia de cuota de intentos local y arranque real mediante el lanzador sin navegador. Las descargas de Instagram y la experiencia visual de Windows/Mac no se han comprobado en una computadora del usuario.
