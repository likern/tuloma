```{=html}
<div class="flow" aria-label="Поток вычислений">
  <div><span>01</span><strong>Точки A и B</strong><small>Координаты и высоты</small></div>
  <div><span>02</span><strong>NumPy</strong><small>Интерполяция и проверка узлов</small></div>
  <div><span>03</span><strong>Видимость</strong><small>Статус и диагностика</small></div>
  <div><span>04</span><strong>SVG</strong><small>График и подпись</small></div>
</div>
<div class="code-lab">
  <div class="code-head"><span><b></b> experiment.py</span><button type="button" class="subtle" id="load-params">Подставить параметры графика</button></div>
  <label class="sr-only" for="source-code">Редактор исходного кода Python</label>
  <textarea id="source-code" spellcheck="false" wrap="off" rows="9">from los import profile_los

# Измените координаты или высоты и запустите снова.
x_a, x_b = 0, 80
h_a, h_b = 0, 0

result = profile_los(x_a, x_b, h_a, h_b)
print(result)</textarea>
  <div class="code-actions"><button type="button" class="primary" id="run-code">Выполнить <span aria-hidden="true">▶</span></button><a href="assets/los.py" download>Скачать los.py</a><a href="assets/experiment.py" download>Скачать пример</a></div>
  <pre class="code-output" id="code-output" role="status" aria-label="Результат Python">При запуске здесь появится вывод Python.</pre>
</div>
<details class="source-details">
  <summary>Проверка узлов и выборка · исходник NumPy</summary>
  <pre class="algorithm-source"><code><!-- los-source --></code></pre>
</details>
```
