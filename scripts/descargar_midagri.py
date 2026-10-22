"""Descarga pública única del archivo enlazado por el portal oficial SIEA."""
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data/raw/midagri'
URL = 'https://drive.usercontent.google.com/download?id=11XHc0X8fQb1u-XcnIPqPQmDPTp9nPUyU&export=download&confirm=t'


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    target = FOLDER / 'MNSA_2024.rar'
    if target.exists() and target.stat().st_size == 401542766:
        print('Archivo nacional ya descargado; se conserva la copia local.')
        return
    record = {'consulta_utc': datetime.now(timezone.utc).isoformat(),
              'portal_oficial': 'https://siea.midagri.gob.pe/herramientas/superficie-agricola',
              'archivo_id': '11XHc0X8fQb1u-XcnIPqPQmDPTp9nPUyU',
              'nombre': 'MNSA_2024.rar', 'bytes_metadatos_drive': 401542766,
              'url_descarga_publica': URL, 'nota': 'Sin redistribución del archivo nacional.'}
    digest, total = hashlib.sha256(), 0
    with urlopen(Request(URL, headers={'User-Agent': 'curso-python/0.1'}), timeout=45) as response:
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            raise RuntimeError('La respuesta es una página HTML, no el archivo nacional; descarga detenida.')
        with (FOLDER / 'MNSA_2024.rar.part').open('wb') as stream:
            while block := response.read(2 * 1024 * 1024):
                total += len(block)
                if total > 600 * 1024 * 1024:
                    raise RuntimeError('Se superó el límite de descarga de 600 MiB.')
                stream.write(block)
                digest.update(block)
                if total % (40 * 1024 * 1024) == 0:
                    print(f'Descargados {total // (1024 * 1024)} MiB.', flush=True)
    if total != record['bytes_metadatos_drive']:
        raise RuntimeError(f'Tamaño inesperado: {total}; se conserva como archivo parcial.')
    (FOLDER / 'MNSA_2024.rar.part').replace(target)
    record.update(bytes=total, sha256=digest.hexdigest(), estado='descargado')
    (ROOT / 'docs/MIDAGRI_ACCESO.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
