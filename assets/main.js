import {readScenario, scenarioUrl} from './state.js';

const $ = (selector, root = document) => root.querySelector(selector);
const lab = document.documentElement.dataset.page === 'laboratory';
const vertexEditor = $('#vertex-editor');
const vertexSelect = $('#vertex-select');
const vertexHeight = $('#vertex-height');
const openLab = $('#open-lab');
const backArticle = $('#back-article');
if (openLab && matchMedia('(max-width: 840px)').matches) $('.rail details').open = false;

const runtimeStatus = $('#runtime-status');
const activate = $('#activate');
const run = $('#run-code');
const editor = $('#source-code');
const consoleOutput = $('#code-output');
const fields = [...document.querySelectorAll('[data-index]')];
const svg = $('.chart');
const resultBar = $('.result-bar');
const presets = $('.presets');
const exactMode = $('#exact-mode');
const compareMode = $('#compare-mode');
const comparison = $('#comparison');
const samplingControls = $('#sampling-controls');
const samplingStep = $('#sampling-step');
const stepButtons = [...samplingControls.querySelectorAll('[data-step]')];
const number = new Intl.NumberFormat('ru-RU', {maximumFractionDigits: 2});
const format = value => number.format(value);

let data, result, inputs, sampleResult, heights, renderedHeights;
let vertexIndex = 4;
let comparing = false;
let stepSize = 25;
let view;
let drawing;
let selected;
let active = false;
let worker;
let requestId = 0;
let nextPoint = 0;
let drag = null;
let dirty = false;
let evaluating = false;
const requests = new Map();

function stopWorker(reason) {
  worker?.terminate();
  worker = undefined;
  for (const {reject, timer} of requests.values()) {
    clearTimeout(timer);
    reject(new Error(reason));
  }
  requests.clear();
  active = false;
  for (const field of fields) field.disabled = true;
  svg.classList.remove('is-live');
  vertexEditor.disabled = true;
  samplingStep.disabled = !selected;
  stepButtons.forEach(button => { button.disabled = !selected; });
  activate.disabled = false;
  activate.hidden = false;
}

function ask(message, timeout) {
  if (!worker) {
    worker = new Worker(new URL('./worker.js', import.meta.url));
    worker.onmessage = ({data: reply}) => {
      const pending = requests.get(reply.id);
      if (!pending) return;
      clearTimeout(pending.timer);
      requests.delete(reply.id);
      if (reply.error) pending.reject(new Error(reply.error));
      else pending.resolve(reply);
    };
    worker.onerror = () => stopWorker('Не удалось запустить рабочий процесс Python.');
  }

  const id = ++requestId;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => stopWorker('Среда Python не ответила вовремя.'), timeout);
    requests.set(id, {resolve, reject, timer});
    worker.postMessage({...message, id});
  });
}

const svgNS = 'http://www.w3.org/2000/svg';
function mark(name, attrs = {}, label) {
  const element = document.createElementNS(svgNS, name);
  for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
  if (label != null) element.textContent = label;
  drawing.append(element);
  return element;
}

function draw() {
  if (!data || !result) return;
  const width = Math.round(svg.clientWidth), height = Math.round(svg.clientHeight);
  if (width < 100 || !height) return;
  const left = width < 430 ? 34 : 49, right = width - 17;
  const top = 30, bottom = height - 42;
  const profile = renderedHeights;
  const highest = Math.max(...profile, result.a[1], result.b[1]);
  const step = highest > 20 ? 10 : 5;
  const max = drag?.vertex != null ? drag.max : step * Math.ceil((highest + 2) / step);
  const sx = x => left + (right - left) * x / 100;
  const sy = z => bottom - (bottom - top) * z / max;
  view = {left, right, top, bottom, sx, sy, max};

  drawing = document.createDocumentFragment();
  svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
  mark('title', {}, 'Геометрическая видимость на профиле');
  for (let z = 0; z <= max; z += step) {
    mark('line', {x1:left, x2:right, y1:sy(z), y2:sy(z), stroke:'var(--chart-grid)'});
    mark('text', {x:left-8, y:sy(z)+4, 'text-anchor':'end'}, z);
  }
  for (const x of width < 460 ? [0,25,50,75,100] : [0,10,20,30,40,50,60,70,80,90,100]) {
    mark('text', {x:sx(x), y:bottom+18, 'text-anchor':'middle'}, x);
  }
  mark('text', {x:left, y:15, class:'axis-title'}, 'Высота, м');
  mark('text', {x:(left+right)/2, y:height-4, class:'axis-title', 'text-anchor':'middle'}, 'Расстояние, м');

  const trace = data.x.map((x, i) => sx(x) + ',' + sy(profile[i])).join(' ');
  mark('polygon', {points: sx(0)+','+bottom+' '+trace+' '+sx(100)+','+bottom, fill:'var(--chart-fill)', opacity:'.88'});
  mark('polyline', {points:trace, fill:'none', stroke:'var(--chart-line)', 'stroke-width':2.1, 'stroke-linejoin':'round'});
  data.x.forEach((x, i) => {
    const chosen = lab && active && i === vertexIndex;
    mark('circle', {cx:sx(x), cy:sy(profile[i]), r:chosen?6:lab?3.6:2,
      fill:lab?'var(--panel)':'var(--chart-line)', stroke:chosen?'var(--selected)':'var(--chart-line)',
      'stroke-width':chosen?2:1, 'data-vertex':lab?i:''});
    if (chosen) mark('circle', {cx:sx(x), cy:sy(profile[i]), r:2, fill:'var(--selected)'});
  });

  const [[ax, az], [bx, bz]] = [result.a, result.b];
  if (ax !== bx) {
    const zAt = x => az + (bz-az)*(x-ax)/(bx-ax);
    mark('line', {x1:sx(ax), x2:sx(bx), y1:sy(az), y2:sy(bz), stroke:'var(--endpoint)', 'stroke-width':2});
    for (const [from, to] of result.below) {
      mark('line', {x1:sx(from), x2:sx(to), y1:sy(zAt(from)), y2:sy(zAt(to)),
        stroke:'var(--panel)', 'stroke-width':3.8});
      mark('line', {x1:sx(from), x2:sx(to), y1:sy(zAt(from)), y2:sy(zAt(to)),
        stroke:'var(--blocked)', 'stroke-width':2, 'stroke-dasharray':'5 3'});
    }
  }

  if (comparing && sampleResult) {
    for (const [x, z] of sampleResult.samples) {
      const px = sx(x), py = sy(z);
      mark('line', {x1:px, x2:px, y1:py, y2:bottom, class:'sample-guide'});
      mark('circle', {cx:px, cy:py, r:4.8, class:'sample-point'});
    }
  }

  if (result.kind === 'blocked' && result.x_peak != null) {
    const x = sx(result.x_peak);
    mark('line', {x1:x, x2:x, y1:sy(result.peak_z), y2:sy(result.peak_z-result.excess),
      stroke:'var(--accent)', 'stroke-width':1.4, 'stroke-dasharray':'3 2'});
    const sampledPeak = comparing && sampleResult?.samples.some(([position]) => Math.abs(position-result.x_peak) < 1e-9);
    mark('circle', {cx:x, cy:sy(result.peak_z), r:sampledPeak?7.5:4.4,
      fill:sampledPeak?'none':'var(--panel)', stroke:'var(--accent)', 'stroke-width':2});
    if (width > 380) {
      const onRight = x > right - 50;
      mark('text', {x:x+(onRight?-8:8), y:sy(result.peak_z)-7, 'text-anchor':onRight?'end':'start',
        'paint-order':'stroke', stroke:'var(--panel)', 'stroke-width':4}, '+'+format(result.excess)+' м');
    }
  }

  for (const [index, [label, x, z, color]] of [
    ['A',ax,az,'var(--endpoint)'], ['B',bx,bz,'var(--target)']
  ].entries()) {
    const px = sx(x), py = sy(z);
    mark('line', {x1:px, x2:px, y1:py, y2:sy(result.ground[index]), stroke:color, 'stroke-width':1.4});
    if (index === 0) mark('circle', {cx:px, cy:py, r:5.5, fill:color, stroke:'var(--panel)', 'stroke-width':1.7});
    else mark('rect', {x:px-5.3, y:py-5.3, width:10.6, height:10.6, fill:color,
      stroke:'var(--panel)', 'stroke-width':1.7});
    mark('text', {x:px+(label==='B' && ax===bx?10:0), y:py-10, 'text-anchor':'middle',
      class:'point-label', 'paint-order':'stroke', stroke:'var(--panel)', 'stroke-width':4}, label);
  }

  const host = svg.closest('los-experiment');
  if (host.paintChart) host.paintChart(svg, drawing);
  else svg.replaceChildren(drawing);
  $('.chart-wrap').classList.add('js-ready');
}

const labels = {blocked:'Цель скрыта', touch:'Касание', visible:'Цель видна', same:'Совпадают координаты'};
function showResult() {
  if (!result) return;
  const {kind, x_peak: x, excess} = result;
  $('strong', resultBar).textContent = labels[kind];
  $('strong', resultBar).dataset.kind = kind;
  $('span', resultBar).textContent = ({
    blocked: 'В точке x = ' + format(x) + ' м рельеф выше отрезка на ' + format(excess) + ' м.',
    touch: x == null ? 'Отрезок совпадает со звеном профиля.' : 'В точке x = ' + format(x) + ' м отрезок касается рельефа.',
    visible: 'Рельеф не пересекает отрезок между A и B.',
    same: 'Выберите разные позиции A и B для этого опыта.'
  })[kind];
  showComparison();
  draw();
}

function showComparison() {
  if (!comparing || !sampleResult) return;
  const {sampled, samples} = sampleResult;
  const missed = result.kind === 'blocked' && (sampled === 'visible' || sampled === 'touch');
  const incomplete = sampled === 'empty' || sampled === 'same';
  const labelsForSamples = {
    blocked:'Найдено перекрытие', touch:'Найдено касание',
    visible:'Перекрытие не найдено', empty:'Нет внутренних отсчётов', same:'Совпадают координаты'
  };
  $('#exact-verdict').textContent = labels[result.kind];
  $('#sampled-verdict').textContent = labelsForSamples[sampled];
  comparison.dataset.missed = String(missed);
  $('#comparison-detail').textContent = missed
    ? 'Выборка пропустила перекрытие. Точная проверка обнаружила его при x = ' + format(result.x_peak) + ' м.'
    : incomplete
      ? 'Для этого положения точек при выбранном шаге сравнивать нечего.'
      : sampled === result.kind
        ? 'В этом случае оба метода дали одинаковый статус.'
        : 'Статусы различаются. Равномерный метод проверяет только свои отсчёты.';
  const positions = samples.map(([x]) => format(x));
  $('#sample-positions').textContent = positions.length > 12
    ? 'Внутренние отсчёты: ' + positions.length + '. Первые 12 от точки A: ' + positions.slice(0, 12).join(', ') + ' м.'
    : positions.length ? 'Внутренние отсчёты от точки A: ' + positions.join(', ') + ' м.' : '';
}

function currentScenario() {
  return {inputs, step:stepSize, comparing, heights};
}

function linkFor(path) {
  return scenarioUrl(path, location.href, currentScenario(), data.z);
}

function updateLinks() {
  if (!data || !inputs || !heights) return;
  if (openLab) openLab.href = linkFor('laboratory.html');
  if (backArticle) backArticle.href = linkFor('los.html#experiment');
  if (lab && !$('#share-url').hidden) $('#share-url').value = linkFor('laboratory.html');
}

function updateFields() {
  fields.forEach((field, index) => {
    field.value = inputs[index];
    field.parentElement.querySelector('output').textContent = format(inputs[index]) + ' м';
  });
  for (const button of presets.children) {
    button.setAttribute('aria-pressed', String(button.dataset.preset === selected));
  }
}

function updateInput(index, value) {
  inputs[index] = value;
  selected = undefined;
  updateFields();
  refreshMode();
}

async function recalculate() {
  if (!active || evaluating) return;
  evaluating = true;
  try {
    while (active && dirty) {
      dirty = false;
      const snapshot = [...inputs];
      const step = comparing ? stepSize : null;
      const profile = [...heights];
      const reply = await ask({kind:'solve', inputs:snapshot, step, heights:profile}, 10000);
      if (!dirty && step === (comparing ? stepSize : null) && snapshot.every((v, i) => v === inputs[i])) {
        renderedHeights = profile;
        sampleResult = step == null ? undefined : reply.result;
        result = sampleResult ? sampleResult.exact : reply.result;
        showResult();
      }
    }
  } catch (error) {
    runtimeStatus.textContent = error.message;
  } finally {
    evaluating = false;
  }
}

function refreshMode() {
  updateLinks();
  if (active) {
    dirty = true;
    void recalculate();
    return;
  }
  const preset = data?.presets.find(item => item.id === selected);
  if (preset) {
    renderedHeights = [...data.z];
    result = preset.result;
    sampleResult = comparing ? {...preset.samples[stepSize], exact: result} : undefined;
  }
  showResult();
}

function setPreset(preset) {
  selected = preset.id;
  inputs = [...preset.inputs];
  heights = [...data.z];
  updateVertex();
  samplingStep.disabled = false;
  stepButtons.forEach(button => { button.disabled = false; });
  updateFields();
  refreshMode();
}

function setMode(compare) {
  comparing = compare;
  sampleResult = undefined;
  samplingControls.hidden = !compare;
  comparison.hidden = !compare;
  $('#legend-samples').hidden = !compare;
  if (compare) {
    $('#exact-verdict').textContent = '';
    $('#sampled-verdict').textContent = '';
    $('#comparison-detail').textContent = 'Сравниваем методы…';
    $('#sample-positions').textContent = '';
  }
  exactMode.setAttribute('aria-pressed', String(!compare));
  compareMode.setAttribute('aria-pressed', String(compare));
  refreshMode();
}

function setStep(step) {
  stepSize = step;
  samplingStep.value = step;
  $('#step-value').textContent = format(step) + ' м';
  for (const button of stepButtons) {
    button.setAttribute('aria-pressed', String(Number(button.dataset.step) === step));
  }
  refreshMode();
}

exactMode.addEventListener('click', () => setMode(false));
compareMode.addEventListener('click', () => setMode(true));
samplingStep.addEventListener('input', () => setStep(samplingStep.valueAsNumber));
stepButtons.forEach(button => button.addEventListener('click', () => setStep(Number(button.dataset.step))));

for (const field of fields) {
  field.addEventListener('input', () => updateInput(Number(field.dataset.index), field.valueAsNumber));
}

async function enable() {
  if (active) return;
  activate.disabled = true;
  runtimeStatus.textContent = 'Загрузка Python и NumPy…';
  try {
    await ready;
    const first = await ask({kind:'solve', inputs:[...inputs], heights:[...heights]}, 30000);
    active = true;
    vertexEditor.disabled = !lab;
    updateVertex();
    if (!result) {
      renderedHeights = [...heights];
      result = first.result;
      showResult();
    }
    fields.forEach(field => { field.disabled = false; });
    samplingStep.disabled = false;
    stepButtons.forEach(button => { button.disabled = false; });
    svg.classList.add('is-live');
    activate.hidden = true;
    runtimeStatus.textContent = 'Python и NumPy готовы.';
    dirty = true;
    void recalculate();
  } catch (error) {
    stopWorker(error.message);
    runtimeStatus.textContent = 'Python не загрузился. Готовые примеры рассчитаны этим же модулем.';
  }
}

activate.addEventListener('click', enable);

function updateVertex() {
  if (!lab || !heights) return;
  vertexSelect.value = vertexIndex;
  vertexHeight.value = heights[vertexIndex];
}

function updateHeight(index, value, syncField = true) {
  if (!active || !Number.isFinite(value)) {
    updateVertex();
    return;
  }
  const height = Math.round(2 * Math.max(0, Math.min(40, value))) / 2;
  const changed = height !== heights[index];
  heights[index] = height;
  if (syncField) updateVertex();
  if (!changed) return;
  selected = undefined;
  updateFields();
  refreshMode();
}

function heightAt(event) {
  const relative = event.clientY - svg.getBoundingClientRect().top;
  return drag.max * (view.bottom-relative) / (view.bottom-view.top);
}

function pointAt(event) {
  const bounds = svg.getBoundingClientRect();
  const horizontal = event.clientX - bounds.left;
  return Math.round(200 * Math.max(0, Math.min(1, (horizontal-view.left)/(view.right-view.left))))/2;
}

svg.addEventListener('pointerdown', event => {
  if (!active || !view) return;
  const bounds = svg.getBoundingClientRect();
  const x = event.clientX-bounds.left, y = event.clientY-bounds.top;
  if (y < view.top-8 || y > view.bottom+8) return;
  const distances = [result.a,result.b].map(([px,pz]) => Math.hypot(x-view.sx(px), y-view.sy(pz)));
  const closest = distances[0] <= distances[1] ? 0 : 1;
  if (lab && distances[closest] >= 12) {
    const vertex = data.x.findIndex((node, i) => Math.hypot(x-view.sx(node), y-view.sy(renderedHeights[i])) < 12);
    if (vertex >= 0) {
      vertexIndex = vertex;
      updateVertex();
      drag = {pointer:event.pointerId, vertex, max:view.max};
      svg.setPointerCapture(event.pointerId);
      draw();
      return;
    }
  }
  const index = distances[closest] < 16 ? closest : nextPoint;
  nextPoint = 1-index;
  drag = {pointer:event.pointerId,index};
  svg.setPointerCapture(event.pointerId);
  updateInput(index, pointAt(event));
});
svg.addEventListener('pointermove', event => {
  if (drag?.pointer !== event.pointerId) return;
  if (drag.vertex != null) updateHeight(drag.vertex, heightAt(event));
  else updateInput(drag.index, pointAt(event));
});
for (const eventName of ['pointerup','pointercancel','lostpointercapture']) {
  svg.addEventListener(eventName, () => {drag = null; draw();});
}
new ResizeObserver(draw).observe(svg);

function installCodeControls() {
  $('#load-params').addEventListener('click', () => {
    const [xa, xb, ha, hb] = inputs;
    const method = comparing ? 'compare_profile_los' : 'profile_los';
    const step = comparing ? ', step=' + stepSize : '';
    editor.value = 'from los import ' + method + '\n\n'
      + 'x_a, x_b = '+xa+', '+xb+'\nh_a, h_b = '+ha+', '+hb+'\n'
      + 'z = ' + JSON.stringify(heights) + '\n\n'
      + 'result = ' + method + '(x_a, x_b, h_a, h_b' + step + ', z=z)\nprint(result)\n';
  });
  run.addEventListener('click', async () => {
    run.disabled = true;
    consoleOutput.textContent = active ? 'Выполнение…' : 'Загрузка Python и NumPy…';
    try {
      const reply = await ask({kind:'run', code:editor.value}, active ? 10000 : 30000);
      consoleOutput.textContent = reply.log?.join('\n') || 'Код выполнен.';
    } catch (error) {
      consoleOutput.textContent = error.message;
    } finally {
      run.disabled = false;
    }
  });
}

function installLabControls() {
  data.x.forEach((position, i) => vertexSelect.append(new Option(format(position) + ' м', i)));
  updateVertex();
  vertexSelect.addEventListener('change', () => {
    vertexIndex = Number(vertexSelect.value);
    updateVertex();
    draw();
  });
  vertexHeight.addEventListener('input', () => {
    if (vertexHeight.validity.valid) updateHeight(vertexIndex, vertexHeight.valueAsNumber, false);
  });
  vertexHeight.addEventListener('change', () => updateHeight(vertexIndex, vertexHeight.valueAsNumber));
  $('#reset-experiment').addEventListener('click', () => {
    vertexIndex = 4;
    setPreset(data.presets[0]);
    setStep(25);
    setMode(true);
    $('#share-status').textContent = 'Восстановлен исходный профиль.';
  });
  $('#share-experiment').addEventListener('click', async () => {
    const url = String(linkFor('laboratory.html'));
    const status = $('#share-status');
    try {
      await navigator.clipboard.writeText(url);
      status.textContent = 'Ссылка на этот сценарий скопирована.';
    } catch {
      const input = $('#share-url');
      input.value = url;
      input.hidden = false;
      input.select();
      status.textContent = 'Скопируйте выделенную ссылку.';
    }
  });
}

const ready = fetch(new URL('./examples.json', import.meta.url))
  .then(response => {
    if (!response.ok) throw new Error('Не удалось загрузить данные опыта.');
    return response.json();
  })
  .then(json => {
    data = json;
    for (const preset of data.presets) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = preset.label;
      button.dataset.preset = preset.id;
      button.addEventListener('click', () => setPreset(preset));
      presets.append(button);
    }
    const initial = data.presets[0];
    const state = readScenario(location.search, {inputs:initial.inputs, heights:data.z}, lab);
    inputs = state.inputs;
    heights = state.heights;
    const standard = heights.every((height, i) => height === data.z[i]);
    selected = standard ? data.presets.find(preset => preset.inputs.every((value, i) => value === inputs[i]))?.id : undefined;
    updateFields();
    setStep(state.step);
    setMode(state.comparing);
    if (!selected) {
      $('.result-bar strong').textContent = 'Профиль из ссылки';
      $('.result-bar span').textContent = 'Ожидаем расчёт для переданных параметров.';
    }
    if (lab) installLabControls();
    installCodeControls();
    if (!selected) void enable();
  })
  .catch(error => { runtimeStatus.textContent = error.message; throw error; });

try {
  const {LitElement, html, render: renderSvg, svg: svgTemplate} = await Promise.race([
    import('https://cdn.jsdelivr.net/npm/lit@3.3.1/+esm'),
    new Promise((_, reject) => setTimeout(reject, 2300))
  ]);
  customElements.define('los-experiment', class extends LitElement {
    render() { return html`<slot></slot>`; }
    paintChart(target, layer) {
      renderSvg(svgTemplate`${[...layer.childNodes]}`, target);
    }
  });
  svg.replaceChildren();
  draw();
} catch {
  // The native controls remain usable when the optional renderer cannot load.
}
