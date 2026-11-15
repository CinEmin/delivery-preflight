# Check an HTML game ZIP before uploading to itch.io

For small HTML projects already exported from an editor or engine. This guide uses the optional, free [Delivery Preflight evaluation download](https://github.com/CinEmin/delivery-preflight/releases/tag/v0.1.1). Python 3.10+ is required for the checker; players do not need Python.

## Choose the upload format

itch.io accepts a self-contained HTML file directly. For a multi-file project, put the entry file and its supporting files in one ZIP. The entry file is named `index.html`; filename case matters, and asset references should be relative. Separate uploads on the project page do not become companion assets. See the [official HTML5 upload documentation](https://itch.io/docs/creators/html5), checked 15 November 2026.

## Inspect the intended layout

For this example, the archive should contain:

```text
index.html
assets/game.js
README.txt
```

The exact required paths are a checklist you supply, not paths the checker discovers from your HTML. If your exported project uses different files, adapt the command. Keep the files together while packaging. Accidentally including an enclosing folder changes `index.html` into `my-game/index.html`, which fails this root-entry check.

## Run the check

From the extracted checker folder:

```sh
python preflight.py game.zip --require index.html --require assets/game.js --require README.txt
```

For the example layout, expect `PASS: 3 entries; integrity checked: True`. A `required_missing` finding names the missing exact path. `Index.html` does not satisfy `index.html`. Rebuild the package after correcting the layout, then rerun the same command. Remove unwanted system metadata and review sensitive-path findings before sharing.

For a machine-readable report:

```sh
python preflight.py game.zip --require index.html --require assets/game.js --json
```

Exit 0 means these checks passed, 1 means warnings, and 2 means errors. A syntactically valid report with errors is still a failed check.

## Then test the actual game

This checker does not parse HTML, JavaScript or CSS references, run your game, test mobile input, or validate every itch.io upload rule. Its resource caps differ from the platform's limits. A pass is not platform approval, malware clearance or proof of working assets.

Preview the uploaded game, start a session, exercise an asset-dependent action, and test the intended controls and screen sizes. A missing reference can still fail at runtime even when every file you listed passed. Consult the current official documentation for file-count, size and path-length limits.

This example uses synthetic files, not customer evidence. Code and documentation are AI-assisted. No third-party game or personal archive is required.
