#!/bin/sh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "Instala Python 3.11 o superior desde https://www.python.org/downloads/"
  read -r answer
  exit 1
fi
python3 iniciar_local.py "$@"
result=$?
if [ "$result" -ne 0 ]; then
  printf '\nNo se pudo iniciar. Pulsa Enter para cerrar.'
  read -r answer
fi
exit "$result"
