# Usar desde el navegador sin ZIP, Python ni instalaciones

El editor ya está en:
https://alvaroporras2002-coder.github.io/video-corrector/

Para descargar reels desde esa página necesita un backend alojado. El repositorio incluye una configuración Render Blueprint que crea un solo servicio en el plan Free; no crea bases de datos ni discos de pago.

## Activar

1. Abre https://render.com/deploy?repo=https://github.com/alvaroporras2002-coder/video-corrector
2. Inicia sesión o crea tu cuenta en Render, y concede acceso al repositorio si el formulario lo solicita. Todo se hace en el navegador.
3. Revisa que el único servicio, `corte-studio-reels`, use el plan **Free**. Confirma con Deploy/Apply, según lo que muestre Render. No necesitas descargar archivos ni configurar comandos.
4. Espera a que el servicio aparezca como **Live**.
5. Copia la URL HTTPS asignada al servicio. No es el enlace del panel de administración ni el enlace de Instagram.
6. En el editor abre Medios → Instagram. Pega esa URL en **URL base del servicio**, pulsa **Comprobar conexión** y espera. Un servidor gratuito inactivo puede tardar alrededor de un minuto en despertar.
7. Pega el reel y pulsa **Descargar e importar**. Si Instagram permite obtenerlo, se añade al editor.

También puedes enviar esa URL al asistente para actualizar config.json y dejarla como conexión predeterminada de la página. El servidor no está desplegado hasta que completes la confirmación en tu propia cuenta de Render.

## Costos y límites

La configuración pide explícitamente el plan Free. No cambies a un plan de pago si quieres mantenerlo gratuito. Render puede aplicar verificaciones de cuenta. Si el formulario exige pago o no te ofrece Free, no confirmes un plan de pago: comparte la pantalla para revisar la opción disponible.

Free tiene cuotas de horas, transferencia y compilación, se suspende por inactividad y puede suspenderse al exceder límites. No es ilimitado ni se garantiza disponibilidad permanente. No se incluyen servicios de pago en este Blueprint. La cuenta y su facturación se administran en Render.

Los límites del descargador alojado siguen siendo hasta 100 MB y cinco minutos por reel, dos descargas simultáneas y seis intentos cada diez minutos por IP. Instagram puede rechazar el acceso incluso a un reel público; no se solicitan cookies, sesiones ni contraseñas.

El enlace del reel se envía a tu servicio Render, que intenta obtener el video. El archivo se importa al almacenamiento del navegador y no se publica en el repositorio. Exportar el resultado a un archivo sigue dependiendo de los permisos de descarga del navegador del trabajo.

## Actualizaciones

Los despliegues automáticos están desactivados para que cada cambio del repositorio no reconstruya el servicio ni consuma minutos de compilación. Si cambian el backend o sus dependencias, usa **Manual Deploy → Deploy latest commit** en Render. No crees otro servicio si ya tienes uno activo: reutiliza su URL.

Documentación oficial:
https://render.com/docs/deploy-to-render
https://render.com/docs/free
