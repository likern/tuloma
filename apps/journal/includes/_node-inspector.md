```{=html}
<div class="node-inspector" id="node-inspector">
<div class="lesson-controls inspector-modes" role="group" aria-label="Источник данных разбора">
<button type="button" data-trace-mode="worked" aria-pressed="true">Учебный пример</button>
<button type="button" data-trace-mode="live" aria-pressed="false">Параметры главного графика</button>
</div>
<p class="lesson-status" id="trace-source">Учебный пример: A — 0 м, B — 80 м, обе высоты — 0 м.</p>
<div class="trace-plots"><div><img src="assets/cover-profile.svg" alt="Исходный профиль и линия визирования."><svg id="trace-profile" role="img" aria-label="Профиль и выбранный узел"></svg></div><div><img src="assets/figures/profile-difference.svg" alt="Разность высот достигает +6 м при x = 40 м."><svg id="trace-difference" role="img" aria-label="Разность высот и выбранный узел"></svg></div></div>
<div class="table-scroll"><table class="trace-table"><caption>Узлы между A и B. Выберите абсциссу, чтобы рассмотреть расчёт.</caption><thead><tr><th scope="col">xᵢ, м</th><th scope="col">zᵢ, м</th><th scope="col">tᵢ</th><th scope="col">z_AB, м</th><th scope="col">dᵢ, м</th></tr></thead><tbody id="trace-rows"><tr data-node="1"><th scope="row"><button type="button" class="node-choice" data-node-index="1" aria-pressed="false">11</button></th><td>2</td><td>0,1375</td><td>6</td><td>-4</td></tr>
<tr data-node="2"><th scope="row"><button type="button" class="node-choice" data-node-index="2" aria-pressed="false">23</button></th><td>0</td><td>0,2875</td><td>6</td><td>-6</td></tr>
<tr data-node="3"><th scope="row"><button type="button" class="node-choice" data-node-index="3" aria-pressed="false">33</button></th><td>3</td><td>0,4125</td><td>6</td><td>-3</td></tr>
<tr data-node="4"><th scope="row"><button type="button" class="node-choice" data-node-index="4" aria-pressed="false">40</button></th><td>12</td><td>0,5</td><td>6</td><td>6</td></tr>
<tr data-node="5"><th scope="row"><button type="button" class="node-choice" data-node-index="5" aria-pressed="false">43</button></th><td>5</td><td>0,5375</td><td>6</td><td>-1</td></tr>
<tr data-node="6"><th scope="row"><button type="button" class="node-choice" data-node-index="6" aria-pressed="false">53</button></th><td>1</td><td>0,6625</td><td>6</td><td>-5</td></tr>
<tr data-node="7"><th scope="row"><button type="button" class="node-choice" data-node-index="7" aria-pressed="false">63</button></th><td>0</td><td>0,7875</td><td>6</td><td>-6</td></tr>
<tr data-node="8"><th scope="row"><button type="button" class="node-choice" data-node-index="8" aria-pressed="false">73</button></th><td>3</td><td>0,9125</td><td>6</td><td>-3</td></tr></tbody></table></div>
<div class="lesson-controls"><button type="button" id="trace-prev">← Предыдущий узел</button><button type="button" id="trace-next">Следующий узел →</button></div>
<p class="trace-detail" id="trace-detail" role="status">Максимум +6 м достигается при x = 40 м.</p>
<p class="lesson-note">Просмотр рассчитанных узлов. NumPy вычисляет массивы целиком; кнопки выбирают строку для объяснения. Операции и значения берутся из Python.</p>
</div>
```
