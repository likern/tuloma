```{=html}
<figure class="experiment-figure" aria-label="Эксперимент с линией визирования">
  <los-experiment>
    <div class="widget-shell">
      <div class="widget-plot">
        <div class="chart-wrap">
          <svg class="chart" role="img" aria-label="Профиль рельефа, линия визирования и отсчёты"></svg>
          <img class="nojs" src="assets/cover-profile.svg" alt="Исходный профиль: вершина на 6 м выше отрезка AB.">
        </div>
        <ul class="chart-legend" aria-label="Обозначения графика">
          <li><i class="legend-a"></i> Наблюдатель A</li>
          <li><i class="legend-b"></i> Цель B</li>
          <li><i class="legend-line"></i> Линия визирования</li>
          <li><i class="legend-blocked"></i> Линия под рельефом</li>
          <li id="legend-samples"><i class="legend-sample"></i> Равномерный отсчёт</li>
        </ul>
        <div class="result-bar" role="status">
          <strong data-kind="blocked">Цель скрыта</strong><span>В точке x = 40 м рельеф выше отрезка на 6 м.</span>
        </div>
        <div id="comparison" class="comparison" hidden aria-live="polite">
          <div class="comparison-pair">
            <div><small>ПО УЗЛАМ ПРОФИЛЯ</small><strong id="exact-verdict"></strong></div>
            <div><small>ПО РАВНОМЕРНЫМ ОТСЧЁТАМ</small><strong id="sampled-verdict"></strong></div>
          </div>
          <p id="comparison-detail"></p>
          <p id="sample-positions"></p>
        </div>
      </div>
      <aside class="widget-controls" aria-label="Параметры эксперимента">
        <p class="eyebrow">ПАРАМЕТРЫ</p>
        <div class="presets" aria-label="Готовые сценарии"></div>
        <div class="method-tabs" role="group" aria-label="Режим проверки">
          <button type="button" id="exact-mode" aria-pressed="true">По узлам</button>
          <button type="button" id="compare-mode" aria-pressed="false" aria-controls="sampling-controls">Сравнить методы</button>
        </div>
        <div id="sampling-controls" class="sampling-controls" hidden>
          <label for="sampling-step">Шаг выборки <output id="step-value" for="sampling-step">25 м</output></label>
          <input type="range" id="sampling-step" min="5" max="50" step="1" value="25">
          <div class="sampling-presets" aria-label="Показательные шаги">
            <button class="subtle" type="button" data-step="25" aria-pressed="true">25 м</button>
            <button class="subtle" type="button" data-step="20" aria-pressed="false">20 м</button>
          </div>
        </div>
        <div class="input-grid">
          <label>Позиция A <output>0 м</output><input disabled type="range" min="0" max="100" step="0.5" value="0" data-index="0"></label>
          <label>Позиция B <output>80 м</output><input disabled type="range" min="0" max="100" step="0.5" value="80" data-index="1"></label>
          <label>Высота A над рельефом <output>0 м</output><input disabled type="range" min="0" max="24" step="0.5" value="0" data-index="2"></label>
          <label>Высота B над рельефом <output>0 м</output><input disabled type="range" min="0" max="24" step="0.5" value="0" data-index="3"></label>
        </div>
        <div class="widget-footer">
          <button type="button" class="primary" id="activate">Запустить Python</button>
          <span id="runtime-status" role="status">Готовые сценарии рассчитаны заранее. Запустите Python для свободного редактирования.</span>
        </div>
        <div class="laboratory-controls">
          <fieldset id="vertex-editor" disabled>
            <legend>Вершина рельефа</legend>
            <div>
              <label>Координата x<select id="vertex-select"></select></label>
              <label>Высота, м<input id="vertex-height" type="number" min="0" max="40" step="0.5"></label>
            </div>
            <small>На графике можно перетащить вершину вверх или вниз.</small>
          </fieldset>
          <div class="laboratory-actions">
            <button type="button" class="subtle" id="reset-experiment">Сбросить</button>
            <button type="button" class="subtle" id="share-experiment">Скопировать ссылку</button>
          </div>
          <input type="url" id="share-url" aria-label="Ссылка на текущий эксперимент" hidden readonly>
          <p id="share-status" role="status"></p>
        </div>
      </aside>
    </div>
  </los-experiment>
  <figcaption>Штрихом отмечена часть линии (AB) под рельефом. Синие кольца показывают равномерные отсчёты.</figcaption>
</figure>
```
