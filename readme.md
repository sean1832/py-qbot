# py‑qbot

Lightweight Python wrapper for qbittorrent post‑processing using FileBot.  
Rename, organize and filter your media files in one go.


## Requirements

- **Python** 3.8+  
- **FileBot** installed & on your `PATH`  
- **qbittorrent**  


## Installation

```bash
git clone https://github.com/sean1832/py-qbot.git
cd py-qbot
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -e .
cp config.json.example config.json
```

Then edit `config.json` to suit your setup.

## Usage
bash:
```bash
py-qbot \
  --config config.json \
  --input /path/to/downloads \
  --name "Naruto" \
  --category anime \
  --filter "s==1" \
  --fuzzy \
  --debug \
  --extra "FILTER:s==1;EXCLUDE:sample|subs"
```
powershell:
```shell
py-qbot `
  --config config.json `
  --input C:\Downloads `
  --name "Naruto" `
  --category anime `
  --filter "s==1" `
  --fuzzy `
  --debug `
  --extra "FILTER:s==1;EXCLUDE:sample|subs"
```

### CLI Arguments

| Flag                | Description                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--config <file>`   | (required) Path to your JSON config                                                                                                                           |
| `-i, --input <dir>` | (required) Directory with media files to rename                                                                                                               |
| `-n, --name <str>`  | (required) Media title or base name                                                                                                                           |
| `-c, --category`    | (required) One of: `anime`, `tv`, `movie`                                                                                                                     |
| `-f, --filter`      | (optional) FileBot filter expression (e.g. `s==1`)                                                                                                            |
| `--fuzzy`           | (optional) Enable fuzzy name matching                                                                                                                         |
| `--debug`           | (optional) Turn on DEBUG‑level logging                                                                                                                        |
| `--extra <args>`    | (optional) Semi‑colon‑separated `key:value` pairs. Supported keys:<br>• `FILTER`: overrides `--filter`  <br>• `EXCLUDE`: pipe‑delimited extra dirs to exclude |

## Inspect Log
After running `py-qbot`, check the log file in the `.log` directory.
It will be named with the current date, e.g. `2023-10-01.log`.

## Examples

**Season 1 of One Piece**

```bash
py-qbot --config config.json --input ~/Downloads/OnePiece \
  --name "One Piece" --category anime --filter "s==1" --fuzzy
```

**Add extra exclude dirs**

```bash
py-qbot ... --extra "EXCLUDE:sample|subs|extra_dir"
```

> In reality, working with qbittorent, you'd likely input this as tags.

## Qbittorent Integration
If you're using qbittorrent, you can set up post‑processing scripts to call `py-qbot` automatically after downloads complete.
Following assume you installed `py-qbot` in a virtual environment and is available in the `/root/py-qbot/venv/bin` directory.

```bash
/root/py-qbot/venv/bin/py-qbot --config /root/py-qbot/config.json --input %F --name %N --category %L --extra %G --fuzzy
```

or shortened:

```bash
/root/py-qbot/venv/bin/py-qbot --config /root/py-qbot/config.json -i %F -n %N -c %L --extra %G --fuzzy
```

where:
- `%F` is the download folder
- `%N` is the torrent name
- `%L` is the category (e.g. `anime`, `tv`, `movie`)
- `%G` is any extra tags you want to pass (e.g. `FILTER:s==1;EXCLUDE:sample|subs`)
