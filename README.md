# Тулома

Авторский интерактивный журнал о математике геопространственных вычислений
и монорепозиторий исследовательских модулей.

| Каталог | Ответственность |
| --- | --- |
| `apps/journal/` | Quarto, статья, интерактивная лаборатория, SVG/JS и ресурсы |
| `tools/journal/` | Сборка журнала и генераторы иллюстраций/айдентики |
| `crates/tuloma-los/` | Независимый Rust-контракт LOS 1.5D; точки ручной реализации алгоритмов |
| `packages/tuloma/` | PyO3/NumPy bindings и Python API `from tuloma import los` |
| `packages/tuloma-reference/` | Существующее эталонное NumPy-ядро статьи и его проверки |
| `tools/browser/` | Сборка того же PyO3-модуля для Pyodide/WASM |
| `tests/browser/` | Общая smoke-проверка импорта и памяти в native Python/Pyodide |
| `docs/los-api.md` | Низкоуровневый контракт, формы результатов и границы поддержки |
| `dist/` | Генерируемый результат сборки; не хранится в Git |

## Статус Rust-модуля

Это **каркас**, а не готовый LOS-движок. Работают конструкторы из массивов,
проверки хранилища, владение NumPy-буферами, интерфейсы и упаковка.
**Все геометрические методы**, включая интерполяцию и равномерный конструктор,
возвращают `NotImplementedError`. Реализация алгоритмов намеренно оставлена автору
в `crates/tuloma-los/src/queries.rs`. Никакой подмены этих методов Python-референсом нет.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install 'maturin==1.16.0' 'numpy==2.3.5' 'pytest==9.2.0'
maturin develop --release --locked --manifest-path packages/tuloma/Cargo.toml
python -m pytest packages/tuloma/tests
cargo test -p tuloma-los --locked
```

```python
import numpy as np
from tuloma import los

x = np.array([0., 1., 3.], dtype=np.float64)
z = np.array([1., -2., 4.], dtype=np.float64)
scene = los.Scene1D(x, z)
assert scene.x is x and scene.z is z
scene.validate()
scene.height(0.5)  # NotImplementedError until implemented in Rust
```

`Scene1D` удерживает исходные объекты NumPy и не сортирует/уплотняет/копирует их.
Профиль локальный, плоский, кусочно-линейный; координаты в метрах. Поддерживаются
точные `numpy.ndarray`, native-endian aligned contiguous `float64`, rank 1.
Внешние изменения между вызовами повторно проверяются; конкурентные изменения
и `resize` во время вызова запрещены. См. [полный контракт](docs/los-api.md).

## Журнал

```bash
python -m pip install -r tools/journal/requirements.txt
./build.sh
python -m http.server 8000 --directory dist
```

Для основной сборки нужен Quarto; сохранён резервный путь через Pandoc.
Сервер отдаёт статические файлы; вычисления статьи выполняются в Pyodide Worker.
Существующее эталонное ядро не изменено: при сборке его исходник копируется
из Python-пакета в скачиваемый `assets/los.py` и используется для иллюстраций.

```bash
python -B -m unittest discover -s packages/tuloma-reference/tests
```

Подробности статьи, библиографии и айдентики: [apps/journal/README.md](apps/journal/README.md).

## Rust в браузере

Нативный wheel нельзя загрузить в браузер. Нужен отдельный wheel для
**Pyodide 0.29.4 / CPython 3.13 / Emscripten 4.0.9**, с тем же Python API.
В этом runtime поставляется NumPy 2.2.5, поэтому нижняя граница native-пакета
зафиксирована как `numpy>=2.2.5,<2.6`.

См. [tools/browser/README.md](tools/browser/README.md). После WASM-сборки и
`./build.sh` модуль доступен из редактора Python статьи, а `rust-smoke.html`
проверяет импорт реального WASM-расширения, общую память и явные заглушки.
Статья продолжает вызывать Python-референс до ручной реализации Rust-алгоритмов.
CI сохраняет WASM/native wheels и собранный журнал как артефакты; публикация не выполняется.
