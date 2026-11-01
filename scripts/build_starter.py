#!/usr/bin/env python3
"""Build the included Android 6 startup helper with local Android SDK/JDK tools."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/starter-source')
    p.add_argument('--build-tools', type=Path, required=True)
    p.add_argument('--android-jar', type=Path, required=True)
    p.add_argument('--java-home', type=Path, default=os.environ.get('JAVA_HOME'))
    p.add_argument('--build-dir', type=Path, required=True, help='Private task work directory; contains signing material')
    p.add_argument('--keystore', type=Path)
    p.add_argument('--password-file', type=Path, help='Private JSON with password; required with --keystore')
    a = p.parse_args()
    if not a.java_home:
        p.error('Supply --java-home or JAVA_HOME')
    if bool(a.keystore) != bool(a.password_file):
        p.error('--keystore and --password-file must be supplied together')
    bt, jdk, src, build = a.build_tools.resolve(), (a.java_home / 'bin').resolve(), a.source.resolve(), a.build_dir.resolve()
    for required in [bt/'aapt', bt/'zipalign', bt/'lib/d8.jar', bt/'lib/apksigner.jar', jdk/'java', jdk/'javac', jdk/'keytool', a.android_jar]:
        if not required.is_file(): p.error('Missing local build dependency: ' + str(required))
    build.mkdir(parents=True, exist_ok=True)
    def run(args, **kwargs):
        subprocess.run([str(x) for x in args], check=True, **kwargs)
    run([bt/'aapt', 'package', '-f', '-m', '-M', src/'AndroidManifest.xml', '-S', src/'res', '-I', a.android_jar, '-F', build/'resources.apk', '-J', build])
    classes, dex = build/'classes', build/'dex'
    classes.mkdir(exist_ok=True); dex.mkdir(exist_ok=True)
    sources = list((src/'src').rglob('*.java')) + list(build.rglob('R.java'))
    run([jdk/'javac', '-encoding', 'UTF-8', '-source', '8', '-target', '8', '-classpath', a.android_jar, '-d', classes, *sources])
    run([jdk/'java', '-cp', bt/'lib/d8.jar', 'com.android.tools.r8.D8', '--min-api', '23', '--lib', a.android_jar, '--output', dex, *classes.rglob('*.class')])
    unsigned, aligned = build/'unsigned.apk', build/'aligned.apk'
    shutil.copyfile(build/'resources.apk', unsigned)
    with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as z: z.write(dex/'classes.dex', 'classes.dex')
    run([bt/'zipalign', '-f', '4', unsigned, aligned])
    private = a.password_file or build/'signing-private.json'
    keystore = a.keystore or build/'starter-keystore.p12'
    if private.exists(): password = json.loads(private.read_text())['password']
    else:
        if a.password_file: p.error('Supplied password file does not exist')
        password = secrets.token_urlsafe(30)
        fd = os.open(private, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f: json.dump({'password': password}, f)
    env = os.environ.copy(); env['TVFILTER_SIGNING_PASSWORD'] = password
    if not keystore.exists():
        if a.keystore: p.error('Supplied keystore does not exist')
        run([jdk/'keytool', '-genkeypair', '-keystore', keystore, '-storetype', 'PKCS12', '-storepass:env', 'TVFILTER_SIGNING_PASSWORD', '-keypass:env', 'TVFILTER_SIGNING_PASSWORD', '-alias', 'tvfilter-starter', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650', '-dname', 'CN=TV Filter Starter'], env=env)
        keystore.chmod(0o600)
    output = build/'电视过滤启动助手_0.1.0.apk'
    run([jdk/'java', '-jar', bt/'lib/apksigner.jar', 'sign', '--ks', keystore, '--ks-key-alias', 'tvfilter-starter', '--ks-pass', 'env:TVFILTER_SIGNING_PASSWORD', '--key-pass', 'env:TVFILTER_SIGNING_PASSWORD', '--min-sdk-version', '23', '--v1-signing-enabled', 'true', '--v2-signing-enabled', 'true', '--out', output, aligned], env=env)
    run([jdk/'java', '-jar', bt/'lib/apksigner.jar', 'verify', '--verbose', output])
    print('APK:', output)
    print('SHA256:', hashlib.sha256(output.read_bytes()).hexdigest())
    print('Keep signing material private for future updates; never commit it.')


if __name__ == '__main__': main()
