"""Create synthetic, harmless before/after delivery examples in a new directory."""
import argparse
import json
from pathlib import Path
import zipfile
from preflight import inspect_zip


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    names=['delivery-before.zip','delivery-fixed.zip','demo-report.json']
    if any((args.output/name).exists() for name in names):
        parser.error('Demo outputs already exist; choose a new directory. Nothing overwritten.')
    samples=[ [('artwork.txt','Synthetic placeholder, not a commercial asset.'),('.DS_Store','Synthetic clutter')],
              [('artwork.txt','Synthetic placeholder, not a commercial asset.'),('README.txt','Open artwork.txt. This is a delivery demonstration.')]]
    for name,entries in zip(names,samples):
        with zipfile.ZipFile(args.output/name,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for filename,content in entries:
                info=zipfile.ZipInfo(filename,date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.create_system=3
                info.external_attr=0o100644<<16
                archive.writestr(info,content)
    report={key:inspect_zip(args.output/name,['README.txt']) for key,name in zip(['before','after'],names)}
    (args.output/names[2]).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Before: missing README and system clutter. After: README added and clutter removed.')
    print('Report: '+str(args.output/names[2]))
    return 0

if __name__=='__main__': raise SystemExit(main())
