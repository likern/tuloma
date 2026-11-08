// ABI/storage check in the actual Pyodide WASM runtime, without Python fallback.
import { loadPyodide } from 'pyodide';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
const root = fileURLToPath(new URL('../../', import.meta.url));
const indexURL = process.env.TULOMA_PYODIDE_INDEX || fileURLToPath(new URL('./node_modules/pyodide/', import.meta.url));
const py = await loadPyodide({indexURL});
await py.loadPackage('numpy');
const manifest = JSON.parse(await readFile(resolve(root, 'apps/journal/assets/wheels/manifest.json'), 'utf8'));
const bytes = await readFile(resolve(root, 'apps/journal/assets/wheels', manifest.filename));
const { createHash } = await import('node:crypto');
if (createHash('sha256').update(bytes).digest('hex') !== manifest.sha256) throw new Error('Wheel checksum mismatch');
// The wheel is ZIP; unpack directly so no installer or dependency resolver can
// replace the wheel or obscure which extension was tested.
py.unpackArchive(new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength), 'zip', {extractDir:'/home/pyodide/tuloma-wheel'});
py.runPython('import sys\nsys.path.insert(0,"/home/pyodide/tuloma-wheel")');
await py.runPythonAsync(await readFile(resolve(root, 'tests/browser/smoke.py'), 'utf8'));
