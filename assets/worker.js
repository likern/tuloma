const releases = [
  'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/',
  'https://unpkg.com/pyodide@0.29.4/',
];

let runtime;

async function initialize() {
  const source = await fetch(new URL('./los.py', self.location.href));
  if (!source.ok) throw new Error('Не удалось загрузить исходник LOS.');
  const pythonSource = await source.text();
  let lastError;
  for (const indexURL of releases) {
    try {
      importScripts(indexURL + 'pyodide.js');
      const py = await self.loadPyodide({ indexURL });
      await py.loadPackage('numpy');
      py.FS.writeFile('/home/pyodide/los.py', pythonSource);
      py.runPython('import sys\nsys.path.insert(0, "/home/pyodide")\nfrom los import profile_los, compare_profile_los');
      return py;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

function toPlain(proxy) {
  if (!proxy || typeof proxy.toJs !== 'function') return proxy;
  try {
    return proxy.toJs({dict_converter: Object.fromEntries, create_proxies: false});
  } finally {
    proxy.destroy();
  }
}

let queue = Promise.resolve();
self.onmessage = ({data}) => {
  queue = queue.then(async () => {
    const {id, kind, inputs, code, step, heights} = data;
    try {
      runtime ??= initialize();
      const py = await runtime;
      if (kind === 'solve') {
        const solve = py.globals.get(step == null ? 'profile_los' : 'compare_profile_los');
        const profile = heights ? py.toPy(heights) : null;
        try {
          const args = step == null ? inputs : [...inputs, step];
          const result = solve.callKwargs(...args, {...(profile ? {z: profile} : {}), diagnostics: true});
          self.postMessage({id, result: toPlain(result)});
        } finally {
          profile?.destroy();
          solve.destroy();
        }
        return;
      }
      const log = [];
      const namespace = py.toPy({});
      py.setStdout({batched: line => log.push(line)});
      py.setStderr({batched: line => log.push(line)});
      try {
        const last = await py.runPythonAsync(code, {globals: namespace});
        if (last && typeof last.destroy === 'function') last.destroy();
        const result = namespace.has('result') ? toPlain(namespace.get('result')) : null;
        self.postMessage({id, result, log});
      } finally {
        namespace.destroy();
      }
    } catch (error) {
      self.postMessage({id, error: String(error.message || error)});
    }
  });
};
