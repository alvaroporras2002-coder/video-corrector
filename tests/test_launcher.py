"""Smoke test of the real loopback launcher; no browser or Instagram requests."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
import urllib.request
import urllib.error

ROOT=Path(__file__).parents[1]
class LauncherSmokeTest(unittest.TestCase):
    def test_real_server_starts_and_serves_editor(self):
        python=ROOT/'.venv-local'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
        if not python.is_file():self.skipTest('Run python iniciar_local.py --check first')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        process=subprocess.Popen([sys.executable,str(ROOT/'iniciar_local.py'),'--no-browser','--port',str(port)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        base=f'http://127.0.0.1:{port}/'
        try:
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                if process.poll() is not None:self.fail('Local launcher exited before becoming ready')
                try:
                    with opener.open(base+'health',timeout=1) as response:info=json.load(response)
                    if info.get('mode')=='local':break
                except (OSError,urllib.error.URLError):time.sleep(.15)
            else:self.fail('Local launcher did not start within 30 seconds')
            with opener.open(base+'config.json',timeout=2) as response:config=json.load(response)
            self.assertEqual(config['instagramServiceUrl'],base.rstrip('/'))
            with opener.open(base,timeout=2) as response:
                self.assertIn('Corte Studio',response.read().decode())
        finally:
            process.terminate()
            try:process.wait(timeout=8)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
