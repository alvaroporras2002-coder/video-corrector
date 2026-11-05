import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

spec=importlib.util.spec_from_file_location('reel_backend',Path(__file__).parents[1]/'backend'/'app.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)

class BackendTests(unittest.TestCase):
    def setUp(self):
        api.hits.clear()
        self.client=TestClient(api.app)
        self.url='https://www.instagram.com/reel/ABC_def123/?igsh=x'
    def test_health(self):
        self.assertEqual(self.client.get('/health').json()['service'],'corte-instagram')
    def test_url_normalization(self):
        self.assertEqual(api.canonical(self.url),('https://www.instagram.com/reel/ABC_def123/','ABC_def123'))
    def test_reject_unrelated_hosts_and_private_routes(self):
        for url in ['http://instagram.com/reel/ABC_def123/','https://instagram.com.evil.test/reel/ABC_def123/','https://user:pw@instagram.com/reel/ABC_def123/','https://instagram.com:444/reel/ABC_def123/','https://instagram.com/p/ABC_def123/']:
            with self.subTest(url=url),self.assertRaises(HTTPException):api.canonical(url)
    def test_reject_unknown_origin_before_download(self):
        with patch.object(api.subprocess,'run') as run:
            response=self.client.post('/api/instagram',json={'url':self.url},headers={'Origin':'https://not-approved.example'})
        self.assertEqual(response.status_code,403);run.assert_not_called()
    def test_success_returns_file_and_removes_temp_directory(self):
        captured=[]
        def download(cmd,**kwargs):
            template=Path(cmd[cmd.index('-o')+1]);target=Path(str(template).replace('%(ext)s','mp4'))
            target.write_bytes(b'test-contract-only-not-a-real-video');captured.append(target.parent)
            self.assertEqual(cmd[-1],'https://www.instagram.com/reel/ABC_def123/')
            return subprocess.CompletedProcess(cmd,0,'','')
        with patch.object(api.subprocess,'run',side_effect=download):
            response=self.client.post('/api/instagram',json={'url':self.url})
        self.assertEqual(response.status_code,200);self.assertIn('video/mp4',response.headers['content-type'])
        self.assertEqual(response.headers['x-reel-code'],'ABC_def123');self.assertFalse(captured[0].exists())
    def test_instagram_error_is_reported(self):
        with patch.object(api.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','blocked')):
            self.assertEqual(self.client.post('/api/instagram',json={'url':self.url}).status_code,502)
    def test_timeout_is_reported(self):
        with patch.object(api.subprocess,'run',side_effect=subprocess.TimeoutExpired([],100)):
            self.assertEqual(self.client.post('/api/instagram',json={'url':self.url}).status_code,504)
    def test_rate_limit(self):
        with patch.object(api.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','')):
            for _ in range(6):self.client.post('/api/instagram',json={'url':self.url})
            self.assertEqual(self.client.post('/api/instagram',json={'url':self.url}).status_code,429)

class LocalModeTests(unittest.TestCase):
    def setUp(self):
        import os
        with patch.dict(os.environ, {'CORTE_LOCAL':'1','ALLOWED_ORIGINS':'http://127.0.0.1:8765,http://localhost:8765'}):
            spec=importlib.util.spec_from_file_location('reel_local',Path(__file__).parents[1]/'backend'/'app.py')
            self.api=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.api)
        self.client=TestClient(self.api.app,base_url='http://127.0.0.1:8765')
    def test_local_config_and_editor(self):
        info=self.client.get('/config.json').json()
        self.assertEqual(info,{'instagramServiceUrl':'http://127.0.0.1:8765','mode':'local'})
        self.assertIn('Corte Studio',self.client.get('/').text)
        self.assertEqual(self.client.get('/health').json()['mode'],'local')
    def test_local_server_does_not_expose_source_files(self):
        self.assertEqual(self.client.get('/backend/app.py').status_code,404)
        self.assertEqual(self.client.get('/iniciar_local.py').status_code,404)
    def test_local_server_rejects_untrusted_host(self):
        self.assertEqual(self.client.get('/health',headers={'Host':'attacker.example'}).status_code,400)
    def test_local_mode_has_no_hosting_attempt_quota(self):
        with patch.object(self.api.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','')):
            responses=[self.client.post('/api/instagram',json={'url':'https://www.instagram.com/reel/ABC_def123/'}) for _ in range(8)]
        self.assertTrue(all(r.status_code==502 for r in responses))

if __name__=='__main__':unittest.main()
