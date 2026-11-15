import unittest, tempfile, zipfile, pathlib, stat, subprocess, sys, json
from preflight import inspect_zip

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=pathlib.Path(self.tmp.name)/'delivery.zip'
    def archive(self, entries):
        with zipfile.ZipFile(self.path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in entries: z.writestr(name,data)
        return self.path
    def codes(self, result): return {x['code'] for x in result['findings']}
    def test_demo(self):
        demo=pathlib.Path(__file__).with_name('demo.py')
        p=subprocess.run([sys.executable,str(demo),self.tmp.name],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads((pathlib.Path(self.tmp.name)/'demo-report.json').read_text())
        self.assertEqual(report['before']['status'],'error')
        self.assertEqual(report['after']['status'],'pass')
        self.assertIn('required_missing',self.codes(report['before']))
        self.assertTrue((pathlib.Path(self.tmp.name)/'delivery-fixed.zip').exists())
    def test_good(self):
        r=inspect_zip(self.archive([('docs/readme.txt','Hello')]), ['docs/readme.txt'])
        self.assertEqual(r['status'],'pass'); self.assertTrue(r['integrity_checked'])
    def test_missing(self):
        self.assertIn('required_missing',self.codes(inspect_zip(self.archive([('a','a')]),['LICENSE.txt'])))
    def test_paths(self):
        for name in ['../escape','/root','C:/file','folder\\file','a/../../b']:
            with self.subTest(name=name):
                self.archive([(name,'x')])
                # Windows ZipInfo normalizes backslashes on write; patch both headers.
                if '\\' in name:
                    self.path.write_bytes(self.path.read_bytes().replace(name.replace('\\','/').encode(),name.encode()))
                self.assertIn('unsafe_path',self.codes(inspect_zip(self.path)))
    def test_collision(self):
        self.assertIn('path_collision',self.codes(inspect_zip(self.archive([('A.txt','x'),('a.txt','y')]))))
    def test_symlink(self):
        i=zipfile.ZipInfo('link'); i.create_system=3; i.external_attr=(stat.S_IFLNK|0o777)<<16
        self.assertIn('symlink',self.codes(inspect_zip(self.archive([(i,'target')]))))
    def test_secrets_and_clutter(self):
        c=self.codes(inspect_zip(self.archive([('.env','SECRET'),('__MACOSX/a','x'),('.git/config','x')])))
        self.assertTrue({'sensitive_path','system_clutter'} <= c)
    def test_malformed(self):
        self.path.write_bytes(b'not a zip'); self.assertEqual(inspect_zip(self.path)['status'],'error')
    def test_limit(self):
        r=inspect_zip(self.archive([('large','x'*1000)]),max_expanded=100)
        self.assertIn('resource_limit',self.codes(r)); self.assertFalse(r['integrity_checked'])
    def test_crc(self):
        with zipfile.ZipFile(self.path,'w') as z: z.writestr('a','UNIQUE_PAYLOAD')
        self.path.write_bytes(self.path.read_bytes().replace(b'UNIQUE_PAYLOAD',b'BROKEN_PAYLOAD'))
        self.assertIn('integrity_error',self.codes(inspect_zip(self.path)))
    def test_corrupt_deflate_cli(self):
        self.archive([('a','compressed payload '*20)])
        raw=bytearray(self.path.read_bytes())
        # First local header is 30 bytes plus one-byte filename, no extra data.
        raw[31]=0x07  # BFINAL=1, BTYPE=3 is a reserved DEFLATE block type.
        self.path.write_bytes(raw)
        p=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('preflight.py')),str(self.path),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2,p.stderr)
        self.assertEqual(p.stderr,'')
        r=json.loads(p.stdout)
        self.assertIn('integrity_error',self.codes(r))
        self.assertFalse(r['integrity_checked'])
    def test_control_path(self):
        r=inspect_zip(self.archive([('line'+chr(10)+'name','x')]))
        self.assertIn('unsafe_path',self.codes(r))
    def test_windows_forbidden(self):
        for name in ['bad?.txt','bad*.txt','bad|.txt']:
            with self.subTest(name=name):
                self.assertIn('windows_incompatible',self.codes(inspect_zip(self.archive([(name,'x')]))))
    def test_cli(self):
        self.archive([('readme.txt','ok')])
        p=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('preflight.py')),str(self.path),'--require','missing','--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2); self.assertEqual(json.loads(p.stdout)['status'],'error')

if __name__=='__main__': unittest.main()
