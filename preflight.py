"""Bounded, read-only ZIP delivery checks. No extraction or network access."""
import argparse
import json
import pathlib
import re
import stat
import zipfile
import zlib


def inspect_zip(path, required=(), max_expanded=128*1024*1024):
    result = {'schema_version': 1, 'status': 'pass', 'integrity_checked': False,
              'entries': 0, 'expanded_bytes': 0, 'findings': []}
    def add(code, path='', severity='error'):
        result['findings'].append({'code': code, 'path': path, 'severity': severity})
    try:
        if pathlib.Path(path).stat().st_size > 64*1024*1024:
            add('resource_limit')
        else:
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                result['entries'] = len(entries)
                result['expanded_bytes'] = sum(i.file_size for i in entries)
                limited = len(entries)>2500 or result['expanded_bytes']>max_expanded
                if limited:
                    add('resource_limit')
                else:
                    seen = set()
                    files = {i.filename for i in entries if not i.is_dir()}
                    for needed in required:
                        if needed not in files: add('required_missing', needed)
                    if not files: add('empty_delivery')
                    for item in entries:
                        name = item.orig_filename
                        parts = name.rstrip('/').split('/')
                        if (name.startswith('/') or '\\' in name or ':' in name
                            or any(ord(c)<32 or ord(c)==127 for c in name)
                            or any(p in ('', '.', '..') for p in parts)):
                            add('unsafe_path', name)
                        key = name.rstrip('/').casefold()
                        if key in seen: add('path_collision', name)
                        seen.add(key)
                        if any(any(c in p for c in '<>"|?*') or p.endswith((' ', '.')) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?',p) for p in parts):
                            add('windows_incompatible', name)
                        if stat.S_ISLNK(item.external_attr >> 16): add('symlink', name)
                        if any(p.casefold() in ('.env','.git') or p.casefold().startswith('.env.') for p in parts):
                            add('sensitive_path', name)
                        if any(p in ('__MACOSX','.DS_Store','Thumbs.db') for p in parts):
                            add('system_clutter', name, 'warning')
                    # A file cannot also be the parent directory of another file.
                    file_keys = {n.casefold().rstrip('/') for n in files}
                    for item in entries:
                        parts = item.filename.rstrip('/').split('/')
                        if any('/'.join(parts[:n]).casefold() in file_keys for n in range(1,len(parts))):
                            add('path_collision',item.filename)
                    read_bytes = 0
                    try:
                        for item in entries:
                            if item.is_dir(): continue
                            with archive.open(item) as stream:
                                while chunk := stream.read(65536):
                                    read_bytes += len(chunk)
                                    if read_bytes > max_expanded:
                                        raise ValueError('expanded byte limit')
                        result['integrity_checked'] = True
                    except ValueError:
                        add('resource_limit')
                    except (zipfile.BadZipFile, zlib.error, RuntimeError, NotImplementedError, EOFError, OSError):
                        add('integrity_error')
    except (OSError, zipfile.BadZipFile, EOFError, ValueError):
        add('unreadable_archive')
    severities = {f['severity'] for f in result['findings']}
    result['status'] = 'error' if 'error' in severities else 'warning' if severities else 'pass'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('--require', action='append', default=[], help='Exact required archive path; repeatable')
    parser.add_argument('--json', action='store_true', help='Machine-readable report')
    args = parser.parse_args()
    report = inspect_zip(args.archive,args.require)
    if args.json:
        print(json.dumps(report,ensure_ascii=True,indent=2))
    else:
        print(f"{report['status'].upper()}: {report['entries']} entries; integrity checked: {report['integrity_checked']}")
        for f in report['findings']:
            print(f"{f['severity']}: {f['code']} {ascii(f['path'])}")
        print('Delivery checks only; not malware scanning or a safety certification.')
    return {'pass':0,'warning':1,'error':2}[report['status']]

if __name__ == '__main__':
    raise SystemExit(main())

