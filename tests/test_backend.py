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

if __name__=='__main__':unittest.main()
