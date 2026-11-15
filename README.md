# Delivery Preflight â€” local prototype

Read-only ZIP delivery checks for digital-file creators. Python 3.10+; no dependencies, accounts, uploads, extraction or network calls.

```sh
python preflight.py delivery.zip --require README.md --require LICENSE.txt
python preflight.py delivery.zip --json
python -m unittest discover -v
```

Exit codes: 0 pass, 1 warning, 2 error. Required paths are exact and case-sensitive. Reports contain archive paths but never file contents.

Checks: traversal/absolute/Windows-incompatible paths, case collisions, file/directory conflicts, symlinks, common sensitive paths, system clutter, required files and streamed CRC integrity. Limits: 64 MiB compressed file, 2,500 entries, 128 MiB expanded data. Limit failures do not claim completed integrity checks. Encrypted/unsupported entries fail integrity checking.

This is not malware scanning, a comprehensive secret scanner, a copyright check, or a safety certificate. A pass only means these checks found no issue. Inspect untrusted archives in an appropriately isolated environment. Python must parse the central directory before entry limits can be applied.

## Commercial experiment, not validated demand

Audience hypothesis: independent creators shipping downloadable assets or templates. Potential value: one repeatable buyer-delivery checklist combining integrity and packaging hygiene. Free archive utilities already check integrity; this is a strong substitute. No price, revenue, willingness to pay or uniqueness is established.

Primary references reviewed 2026-11-15: https://www.7-zip.org/faq.html (integrity errors); https://itch.io/docs/creators/html5 (ZIP packaging requirements). These establish existing tooling and packaging requirements, not customer demand.

A synthetic before/after demonstration and a free public trial are available. Real customer usefulness and paid demand remain unverified. Do not build paid integrations or open accounts on this evidence. No open-source license is granted for this repository. Public source availability does not imply permission to redistribute, modify or sell it. RecallKit is a separate project with separate licensing. The downloadable prototype is offered for local evaluation.

## Try the demonstration

Run `python demo.py demo-output` from this folder. It writes two synthetic ZIPs and `demo-report.json`, refusing to overwrite existing outputs. The first ZIP lacks README.txt and includes system clutter. The corrected ZIP adds instructions and removes clutter. This demonstration is not customer evidence.

## Fix a finding

| Code | Action |
|---|---|
|required_missing | Add the exact file at the requested path, or correct your requirement. |
|unsafe_path / windows_incompatible | Rename entries to portable relative paths without traversal, drive letters or reserved names. |
|path_collision | Give files unique case-insensitive paths; avoid file/directory conflicts. |
|sensitive_path | Remove credentials or repository internals; if real secrets were published, revoke them. |
|system_clutter | Rebuild without operating-system metadata. |
|symlink | Replace links with intended regular files where appropriate. |
|integrity_error / unreadable_archive | Rebuild the ZIP; check that it is complete and uses supported, unencrypted compression. |
|resource_limit | Split a large delivery into smaller packages; integrity checking did not finish. |
|empty_delivery | Include the actual buyer files. |

After correcting the source package, rebuild and rerun the same command. The tool never edits your archive.

## Report a problem

You may open an issue describing your Python version, operating system, command, and finding code. Do not upload private archives, file contents, credentials or customer data. Use a small synthetic example where possible. No response-time promise or payment is offered.
