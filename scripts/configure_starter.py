#!/usr/bin/env python3
"""Enable or restore only the startup helper; preserve other accessibility services.

Run only after the user authorizes installing/enabling this accessibility service.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

HELPER = 'io.github.hankun1989.tvfilterstarter/io.github.hankun1989.tvfilterstarter.StarterService'
PACKAGE = HELPER.split('/')[0]


def is_helper(value):
    return value in (HELPER, PACKAGE + '/.StarterService')


def entries(raw):
    return [x for x in raw.split(':') if x and x != 'null']


def enabled_list(raw):
    values = entries(raw)
    if not any(is_helper(x) for x in values): values.append(HELPER)
    return ':'.join(values)


def restored_list(raw, originally_present):
    return raw if originally_present else ':'.join(x for x in entries(raw) if not is_helper(x))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--serial', required=True)
    p.add_argument('--state-file', type=Path, required=True, help='Private task work JSON; never publish')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--enable', action='store_true')
    mode.add_argument('--restore', action='store_true')
    a = p.parse_args()
    def adb(*args):
        r = subprocess.run(['adb', '-s', a.serial, *args], capture_output=True, text=True, errors='replace', timeout=25, check=True)
        if r.stderr.strip(): print(r.stderr.strip())
        return r.stdout.strip()
    def get(key): return adb('shell', 'settings get secure ' + key)
    def put(key, value):
        adb('shell', 'settings put secure ' + key + ' ' + shlex.quote(value))
        if get(key) != value: raise RuntimeError('Setting readback did not match; use the saved state to restore')
    if adb('get-state') != 'device': p.error('Device must be connected and authorized')
    current = get('enabled_accessibility_services')
    master = get('accessibility_enabled')
    if a.state_file.exists():
        state = json.loads(a.state_file.read_text())
        if state.get('serial') != a.serial or state.get('helper') != HELPER: p.error('State file belongs to another device/helper')
    elif a.restore:
        p.error('Restore requires the original state file')
    else:
        if not adb('shell', 'pm path ' + PACKAGE).startswith('package:'): p.error('Install and verify the helper APK first')
        state = {'serial': a.serial, 'helper': HELPER, 'original_services': current, 'original_master': master,
                 'originally_present': any(is_helper(x) for x in entries(current))}
        a.state_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(a.state_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f: json.dump(state, f, ensure_ascii=False, indent=2)
    if a.enable:
        value = enabled_list(current)
        if value != current: put('enabled_accessibility_services', value)
        if master != '1': put('accessibility_enabled', '1')
        print('Helper enabled; other service entries preserved. Verify binding, actual full reboot and video playback.')
    else:
        value = restored_list(current, state['originally_present'])
        if value != current: put('enabled_accessibility_services', value)
        # Do not disable services that the user enabled after our snapshot.
        if state['original_master'] != '1' and master == '1' and (not entries(value) or entries(value) == entries(state['original_services'])):
            put('accessibility_enabled', '0')
        print('Helper settings restored within the saved scope; other current services preserved.')
        print('This does not stop CMFA. Stop it separately if you want filtering off.')


if __name__ == '__main__': main()
