# Вариант №27 — визуализатор графа npm-зависимостей

CLI-приложение получает прямые зависимости npm-пакетов, строит достижимый граф обходом BFS (очередь обрабатывается рекурсивно), находит обратные зависимости и формирует диаграмму D2.

## Требования

- Python 3.10+
- PyYAML (используется только для чтения YAML-конфигурации)
- D2 CLI для экспорта PNG (не участвует в получении зависимостей)

Получение зависимостей реализовано самостоятельно через стандартные `urllib` и `json`. `npm`, `pip`-пакеты для чтения зависимостей, а также сторонние npm API-клиенты не используются.

## Запуск в VS Code

1. Откройте папку проекта `variant27-npm-graph` в VS Code.
2. Откройте Terminal → New Terminal.
3. Создайте виртуальное окружение:
   - Windows: `py -m venv .venv` и `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` и `source .venv/bin/activate`
4. Установите зависимость конфигурации: `python -m pip install -r requirements.txt`
5. Запустите тестовый режим: `python -m src.main --show-config`
6. Обратные зависимости: `python -m src.main --reverse`
7. Проверка тестов: `python -m unittest discover -s tests -v`

## Настройка тестового режима

В `config.yaml` по умолчанию:
```yaml
package_name: A
repository_url: ""
test_repository_file: data/test_graph.json
test_mode: true
max_depth: 3
show_reverse: false
```

Тестовый граф задаётся JSON-объектом: ключ — пакет, значение — список его прямых зависимостей. Для тестового режима имена пакетов должны состоять из заглавных латинских букв. В примере намеренно присутствует цикл `G -> A`.

## Реальный npm-режим

Измените `config.yaml`, например:
```yaml
package_name: lodash
repository_url: https://registry.npmjs.org
test_repository_file: data/test_graph.json
test_mode: false
max_depth: 2
show_reverse: false
```
Приложение получает metadata по адресу `repository_url/ИМЯ_ПАКЕТА` и читает `dependencies` из версии, помеченной npm registry как `latest`. Поэтому в `repository_url` указывается базовый адрес registry: `https://registry.npmjs.org`. Для scoped-пакетов также поддерживается имя вида `@scope/name`.

## D2

Установите D2 CLI по официальной инструкции: https://d2lang.com/tour/install/.
Приложение всегда сохраняет исходник диаграммы в `output/ИМЯ_dependencies.d2`. Если D2 установлен и доступен в PATH, дополнительно создаётся SVG.

## Этапы и коммиты

Сделайте пять коммитов по мере выполнения этапов. Удобнее начать с первого этапа и добавлять файлы постепенно; готовый проект уже содержит итоговую реализацию.

Примеры сообщений:
1. `feat: add YAML configuration and CLI prototype`
2. `feat: fetch direct npm dependencies`
3. `feat: build dependency graph with recursive BFS`
4. `feat: add reverse dependency analysis`
5. `feat: generate D2 dependency visualization`

Чтобы преподаватель видел именно пять этапов, можно добавлять файлы поэтапно и делать коммит после каждого этапа, а не загружать весь итоговый проект одним коммитом.

## Сравнение со штатными средствами

Для выбранного npm можно сравнить список прямых/транзитивных зависимостей с `npm view ИМЯ dependencies` и `npm ls --all` в отдельном контрольном проекте. Возможные расхождения: приложение анализирует поле `dependencies` опубликованной latest-версии; `npm ls` показывает фактически установленное дерево с учётом lock-файла, peer/optional/dev dependencies, платформенных условий и дедупликации. Поэтому результаты могут отличаться.
