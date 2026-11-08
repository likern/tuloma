const ranges = [[0, 100], [0, 100], [0, 24], [0, 24]];
const inputKeys = ['a', 'b', 'ha', 'hb'];

function numberInRange(raw, min, max, precision = 2) {
  const number = Number(raw);
  return raw != null && raw.trim() !== '' && Number.isFinite(number)
    && number >= min && number <= max && Number.isInteger(number * precision)
    ? number : undefined;
}

export function readScenario(search, initial, defaultComparison) {
  const params = new URLSearchParams(search);
  const inputs = inputKeys.map((name, i) => numberInRange(params.get(name), ...ranges[i]) ?? initial.inputs[i]);
  const step = numberInRange(params.get('step'), 5, 50, 1) ?? 25;
  const rawHeights = params.get('z')?.split(',') ?? [];
  const parsedHeights = rawHeights.map(value => numberInRange(value, 0, 40));
  const heights = parsedHeights.length === initial.heights.length && parsedHeights.every(value => value != null)
    ? parsedHeights : [...initial.heights];
  const method = params.get('method');
  const comparing = method === 'compare' || (method !== 'nodes' && defaultComparison);
  return {inputs, step, heights, comparing};
}

export function scenarioUrl(path, base, {inputs, step, heights, comparing}, defaultHeights) {
  const url = new URL(path, base);
  inputKeys.forEach((key, i) => url.searchParams.set(key, inputs[i]));
  url.searchParams.set('step', step);
  url.searchParams.set('method', comparing ? 'compare' : 'nodes');
  if (heights.some((value, i) => value !== defaultHeights[i])) {
    url.searchParams.set('z', heights.join(','));
  }
  return url;
}
