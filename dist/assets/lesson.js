// Teaching views consume Python results; this module only selects and draws them.
const $ = selector => document.querySelector(selector);
const ns = 'http://www.w3.org/2000/svg';
const number = new Intl.NumberFormat('ru-RU', {maximumFractionDigits:4});
const fmt = value => value !== 0 && Math.abs(value) < 0.0001
  ? value.toExponential(2).replace('.', ',').replace('-', '−')
  : number.format(value).replace('-', '−');
const colors = {blocked:'var(--blocked)', touch:'var(--selected)', visible:'var(--visible)'};
let lesson, latest, proofCase = 0, mode = 'worked', position = 3;

function node(tag, attrs = {}, text) {
  const e = document.createElementNS(ns, tag);
  for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,v);
  if (text != null) e.textContent = text;
  return e;
}

function plot(svg, {xDomain, yDomain, xTicks, yTicks, xTitle, yTitle, lines, dots = [], labels = []}) {
  const width = Math.round(svg.clientWidth), height = Math.round(svg.clientHeight);
  if (width < 100 || !height) return;
  const left=46, right=width-16, top=33, bottom=height-40;
  const sx=x=>left+(right-left)*(x-xDomain[0])/(xDomain[1]-xDomain[0]);
  const sy=y=>bottom-(bottom-top)*(y-yDomain[0])/(yDomain[1]-yDomain[0]);
  const frag=document.createDocumentFragment();
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  frag.append(node('title',{},svg.getAttribute('aria-label')));
  for(const y of yTicks){
    frag.append(node('line',{x1:left,x2:right,y1:sy(y),y2:sy(y),stroke:'var(--chart-grid)'}));
    frag.append(node('text',{x:left-7,y:sy(y)+4,'text-anchor':'end'},fmt(y)));
  }
  for(const x of xTicks) frag.append(node('text',{x:sx(x),y:bottom+18,'text-anchor':'middle'},fmt(x)));
  frag.append(node('text',{x:left,y:16,class:'lesson-axis-title'},yTitle));
  frag.append(node('text',{x:(left+right)/2,y:height-4,'text-anchor':'middle'},xTitle));
  for(const line of lines) frag.append(node('polyline',{
    points:line.points.map(([x,y])=>`${sx(x)},${sy(y)}`).join(' '),fill:'none',
    stroke:line.color??'var(--chart-line)','stroke-width':line.width??2,
    ...(line.dash?{'stroke-dasharray':line.dash}:{})
  }));
  for(const dot of dots) frag.append(node('circle',{cx:sx(dot.x),cy:sy(dot.y),r:dot.r??4,
    fill:dot.fill??'var(--panel)',stroke:dot.color??'var(--selected)','stroke-width':2}));
  for(const label of labels){
    const x=sx(label.x), anchor=x<left+55?'start':x>right-55?'end':'middle';
    frag.append(node('text',{x,y:sy(label.y)-11,'text-anchor':anchor,class:'lesson-point-label'},label.text));
  }
  svg.replaceChildren(frag);
}

function drawLine(){
  if(!lesson) return;
  const p=lesson.interpolation[Number($('#line-t').value)];
  $('#line-t-value').textContent=fmt(p.t);
  $('#line-point').textContent=`t = ${fmt(p.t)}; x = ${fmt(p.x)} м; z = ${fmt(p.z)} м.`;
  plot($('#line-demo-svg'),{xDomain:[10,30],yDomain:[0,14],xTicks:[10,20,30],yTicks:[0,4,8,12],
    xTitle:'Горизонтальная координата x, м',yTitle:'Высота z, м',
    lines:[{points:[[10,4],[30,12]],color:'var(--endpoint)'},
           {points:[[10,4],[p.x,4],[p.x,p.z]],color:'var(--line)',dash:'4 3',width:1}],
    dots:[{x:10,y:4,color:'var(--endpoint)'},{x:30,y:12,color:'var(--endpoint)'},
          {x:p.x,y:p.z,r:5,color:'var(--accent)'}],
    labels:[{x:10,y:4,text:'A (10; 4)'},{x:30,y:12,text:'B (30; 12)'}]});
}

function drawProof(){
  if(!lesson) return;
  const example=lesson.proofs[proofCase], p=example.points[Number($('#proof-u').value)];
  $('#proof-u-value').textContent=fmt(p.u);
  $('#proof-point').textContent=`d(a) = ${fmt(example.left)} м; d(b) = ${fmt(example.right)} м; d(x) = ${fmt(p.value)} м.`;
  for(const [i,b] of [...$('#proof-cases').children].entries())b.setAttribute('aria-pressed',String(i===proofCase));
  plot($('#proof-demo-svg'),{xDomain:[0,1],yDomain:[-4,4],xTicks:[0,.5,1],yTicks:[-3,0,3],
    xTitle:'Доля участка u',yTitle:'Разность d(x), м',
    lines:[{points:[[0,0],[1,0]],color:'var(--muted)',width:1},
           {points:[[0,example.left],[1,example.right]],color:'var(--endpoint)'}],
    dots:[{x:p.u,y:p.value,r:5,color:colors[p.kind]}]});
}

function scenario(){return mode==='live' && latest?.result.diagnostics ? latest : lesson.worked;}
function renderInspector(rebuild=true){
  if(!lesson)return;
  const current=scenario(), r=current.result, trace=r.diagnostics, nodes=trace.nodes;
  position=Math.max(0,Math.min(position,nodes.length-1));
  const chosen=nodes[position], params=trace.inputs;
  for(const b of document.querySelectorAll('[data-trace-mode]'))b.setAttribute('aria-pressed',String(b.dataset.traceMode===mode));
  const origin=mode==='worked'?'Учебный пример':latest?.result.diagnostics?'Параметры главного графика':'Ожидаем данные главного графика; пока показан учебный пример';
  $('#trace-source').textContent=`${origin}: A — ${fmt(params[0])} м, B — ${fmt(params[1])} м; h_A = ${fmt(params[2])} м, h_B = ${fmt(params[3])} м. ${current.source==='runtime'?'Рассчитано Python в браузере.':'Рассчитано Python при сборке.'}`;
  if(rebuild){
    const body=document.createDocumentFragment();
    for(const n of nodes){
      const row=document.createElement('tr'); row.dataset.node=n.index;
      const th=document.createElement('th');th.scope='row';
      const button=document.createElement('button');button.type='button';button.className='node-choice';
      button.dataset.nodeIndex=n.index;button.textContent=fmt(n.x);
      button.setAttribute('aria-label',`Рассмотреть узел x = ${fmt(n.x)} м`);th.append(button);row.append(th);
      for(const value of [n.z,n.t,n.line_z,n.gap]){const td=document.createElement('td');td.textContent=fmt(value);row.append(td);}
      body.append(row);
    }
    if(!nodes.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='Внутренних узлов нет: применяется отдельная ветвь алгоритма.';tr.append(td);body.append(tr);}
    $('#trace-rows').replaceChildren(body);
  }
  for(const b of $('#trace-rows').querySelectorAll('button')){
    const selected=chosen?.index===Number(b.dataset.nodeIndex);
    b.setAttribute('aria-pressed',String(selected));b.closest('tr').classList.toggle('is-selected',selected);
  }
  $('#trace-prev').disabled=!nodes.length||position===0;
  $('#trace-next').disabled=!nodes.length||position===nodes.length-1;
  $('#trace-detail').textContent=chosen
    ? `Узел ${position+1} из ${nodes.length}: x = ${fmt(chosen.x)} м. t = ${fmt(chosen.t)}; z_AB = ${fmt(chosen.line_z)} м; d = ${fmt(chosen.gap)} м. Максимум среди просмотренных узлов: ${fmt(chosen.running_max)} м.`
    : r.kind==='same'?'Одинаковые абсциссы: демонстрация возвращает служебный статус same.':'Отрезок принадлежит одному звену. Ответ определяется высотами концов.';
  const source=$('#alg-profile-los');
  for(const line of source.querySelectorAll('.algorithm-line'))line.classList.toggle('is-teaching-active',Boolean(chosen)&&[15,16,17].some(i=>line.id===`alg-profile-los-L${i}`));

  const profile=current.x.map((x,i)=>[x,current.z[i]]), top=Math.max(10,...current.z,r.a[1],r.b[1])+3;
  plot($('#trace-profile'),{xDomain:[0,100],yDomain:[Math.min(0,...current.z),top],xTicks:[0,50,100],yTicks:[0,Math.round(top/2),Math.round(top)],
    xTitle:'Расстояние x, м',yTitle:'Профиль и линия AB, м',
    lines:[{points:profile},{points:[r.a,r.b],color:'var(--endpoint)'},...(chosen?[{points:[[chosen.x,chosen.z],[chosen.x,chosen.line_z]],color:'var(--selected)',dash:'3 2'}]:[])],
    dots:chosen?[{x:chosen.x,y:chosen.z,r:5,color:'var(--selected)'}]:[]});
  const diffs=trace.difference;
  const xs=diffs.map(p=>p[0]), ys=diffs.map(p=>p[1]);
  const left=xs.length?Math.min(...xs):params[0]-1, right=xs.length?Math.max(...xs):params[1]+1;
  const low=Math.min(-1,...ys)-1, high=Math.max(1,...ys)+1;
  plot($('#trace-difference'),{xDomain:[left,right],yDomain:[low,high],xTicks:[left,(left+right)/2,right],yTicks:[Math.ceil(low),0,Math.floor(high)],
    xTitle:'Расстояние x, м',yTitle:'Разность d(x), м',
    lines:[{points:[[left,0],[right,0]],color:'var(--muted)',width:1},{points:diffs,color:'var(--accent)'}],
    dots:chosen?[{x:chosen.x,y:chosen.gap,r:5,color:colors[chosen.kind]}]:[]});
}

function choose(pos){
  const nodes=scenario().result.diagnostics.nodes;
  position=Math.max(0,Math.min(pos,nodes.length-1));renderInspector(false);
  if(nodes[position])document.dispatchEvent(new CustomEvent('los:select-node',{detail:{x:nodes[position].x}}));
}

document.addEventListener('los:result',event=>{
  const changed=latest?.result!==event.detail.result;
  latest=event.detail;
  if(lesson && mode==='live' && changed)renderInspector();
});

try{
  const response=await fetch(new URL('./lesson-data.json',import.meta.url));
  if(!response.ok)throw new Error('Не удалось загрузить данные иллюстраций.');
  lesson=await response.json();
  for(const id of ['line-demo','proof-demo','node-inspector'])$('#'+id).classList.add('lesson-ready');
  for(const input of [$('#line-t'),$('#proof-u')])input.disabled=false;
  $('#line-t').addEventListener('input',drawLine);$('#proof-u').addEventListener('input',drawProof);
  lesson.proofs.forEach((p,i)=>{
    const b=document.createElement('button');b.type='button';b.textContent=p.title;
    b.addEventListener('click',()=>{proofCase=i;drawProof();});$('#proof-cases').append(b);
  });
  for(const b of document.querySelectorAll('[data-trace-mode]'))b.addEventListener('click',()=>{mode=b.dataset.traceMode;renderInspector();});
  $('#trace-rows').addEventListener('click',event=>{
    const b=event.target.closest('button[data-node-index]');if(!b)return;
    choose(scenario().result.diagnostics.nodes.findIndex(n=>n.index===Number(b.dataset.nodeIndex)));
  });
  $('#trace-prev').addEventListener('click',()=>choose(position-1));
  $('#trace-next').addEventListener('click',()=>choose(position+1));
  for(const b of document.querySelectorAll('[data-reset-example]'))b.addEventListener('click',()=>{
    document.dispatchEvent(new Event('los:reset-example'));mode='worked';position=3;renderInspector();
  });
  for(const a of document.querySelectorAll('[data-compare-step]'))a.addEventListener('click',()=>{
    document.dispatchEvent(new CustomEvent('los:compare-example',{detail:{step:Number(a.dataset.compareStep)}}));
  });
  const redraw=()=>{drawLine();drawProof();renderInspector(false);};
  const observer=new ResizeObserver(redraw);
  for(const id of ['line-demo-svg','proof-demo-svg','trace-profile','trace-difference'])observer.observe($('#'+id));
  drawLine();drawProof();renderInspector();
  document.dispatchEvent(new Event('los:request-state'));
}catch(error){
  const status=document.createElement('p');status.className='lesson-note';status.textContent='Интерактивные иллюстрации недоступны. Статические рисунки и учебная таблица сохранены.';
  $('#line-demo').append(status);
  console.error(error);
}

// A small, accessible active-section indicator for the long article.
const links=[...document.querySelectorAll('.rail nav a')];
const headings=links.map(a=>document.getElementById(a.hash.slice(1))).filter(Boolean);
function updateRail(){
  let active=headings[0];for(const h of headings)if(h.getBoundingClientRect().top<160)active=h;
  for(const a of links){if(a.hash==='#'+active?.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}
}
document.addEventListener('scroll',updateRail,{passive:true});updateRail();
