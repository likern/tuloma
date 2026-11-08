// Load the same PyO3 extension used by native Python into Pyodide 0.29.4.
self.loadTulomaNative = async function(py, {optional = false} = {}) {
  const base = new URL('./wheels/', self.location.href);
  const response = await fetch(new URL('manifest.json', base));
  if (response.status === 404 && optional) return false;
  if (!response.ok) throw new Error('Build the Tuloma WASM wheel before loading the native module.');
  const manifest = await response.json();
  if (manifest.pyodide !== '0.29.4' || !/^[A-Za-z0-9_.-]+\.whl$/.test(manifest.filename)) {
    throw new Error('Unsupported Tuloma wheel manifest.');
  }
  const wheel = await fetch(new URL(manifest.filename, base));
  if (!wheel.ok) throw new Error('Tuloma WASM wheel is missing.');
  const bytes = new Uint8Array(await wheel.arrayBuffer());
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
  const hash = Array.from(digest, x => x.toString(16).padStart(2, '0')).join('');
  if (hash !== manifest.sha256) throw new Error('Tuloma wheel checksum mismatch.');
  const path = '/tmp/' + manifest.filename;
  py.FS.writeFile(path, bytes);
  await py.loadPackage('micropip');
  try {
    await py.runPythonAsync('import micropip\nawait micropip.install(' + JSON.stringify('emfs:' + path) + ', deps=False)');
  } finally {
    py.FS.unlink(path);
  }
  return true;
};
