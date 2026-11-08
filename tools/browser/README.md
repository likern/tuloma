# PyO3/NumPy в браузере

Собирается **тот же** `tuloma._los`, а не отдельный JS-backend.
Версии привязаны к существующему журналу:

| Компонент | Версия |
| --- | --- |
| Pyodide | 0.29.4 |
| Python ABI | CPython 3.13 |
| NumPy внутри Pyodide | 2.2.5 |
| Emscripten | 4.0.9 |
| Rust target | wasm32-unknown-emscripten |
| Rust для WASM | nightly-2025-02-01 + upstream wasm-EH sysroot |
| pyodide-build | 0.39.1 |
| maturin | 1.16.0 |

Нативная Rust-сборка отдельно использует rust-toolchain.toml. Менять глобальный
default toolchain не нужно. Emscripten exceptions и обычный Rust sysroot
несовместимы: setup устанавливает pinned wasm-EH sysroot из официального релиза.
Документы: [ABI 313](https://pyodide.org/en/0.29.4/development/abi/313.html),
[Rust tutorial](https://pyodide-build.readthedocs.io/en/latest/tutorials/rust.html).

## Сборка

В отдельном окружении Python 3.13, из корня репозитория:

```bash
python3.13 -m venv .venv-wasm
source .venv-wasm/bin/activate
python -m pip install -r tools/browser/requirements.txt
./tools/browser/build.sh
```

Нужен установленный rustup. Скрипт загружает cross-build environment,
Emscripten SDK и конкретный Rust toolchain/sysroot в пользовательские кеши.
`PYODIDE_XBUILDENV_PATH` можно задать явно; default - `.cache/pyodide`.
Архив Rust sysroot кешируется в `.cache/sysroots` и каждый раз проверяется по SHA-256.
Wheel создаётся в `.cache/wasm-wheels`; stage.py копирует его в генерируемый
`apps/journal/assets/wheels` вместе с manifest и SHA-256. Нативный wheel
не принимается этим скриптом. Сгенерированные бинарники не коммитятся.

## Проверки

```bash
npm ci --prefix tools/browser
npm test --prefix tools/browser
```

Это запускает реальный Pyodide/WASM runtime в Node, импортирует .so из wheel,
проверяет общую память NumPy и ожидаемый NotImplementedError без Python fallback.

Для настоящего браузера затем из native build-окружения Python:

```bash
./build.sh
python -m http.server 8000 --directory dist
```

Откройте `http://localhost:8000/rust-smoke.html` и запустите проверку.
Она работает в том же Worker, что и статья. Worker при наличии manifest
проверяет hash, устанавливает wheel в Pyodide и позволяет вызывать
`from tuloma import los` в редакторе Python статьи. Заглушки не заменяют
существующий эталонный расчёт графика.

`file://` не поддерживается. Zero-copy проверяется на границе Python/Rust
в одной linear memory; JS/Worker сообщения и визуализация - другая граница.

CI собирает wheel и журнал и сохраняет артефакты. Автоматической публикации,
изменения аудитории или обновления размещённого сайта нет.
