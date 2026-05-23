# 🤝 Contributing to ai-reviewer

Спасибо за интерес к проекту! Вот как можно помочь:

## 🚀 Быстрый старт

```bash
git clone https://github.com/твой-ник/ai-reviewer.git
cd ai-reviewer
pip install -e .
pip install pytest pytest-cov
```

## 📝 Что можно сделать

### 1. Добавить правила безопасности

Добавь новые паттерны в `fast_analyze()`:

```python
# Пример: проверка на CSRF
if re.search(r"@csrf_exempt", line):
    issues.append({
        "severity": "warning",
        "type": "csrf",
        "message": "CSRF защита отключена"
    })
```

### 2. Поддержать новый язык

Добавь расширение в `scan_files()`:

```python
extensions = {
    # ... существующие ...
    ".php": "php",
    ".rb": "ruby",
}
```

### 3. Добавить AI провайдер

Отредактируй `cloud_client.py`:

```python
"myprovider": {
    "base_url": "https://api.myprovider.com/v1",
    "default_model": "my-model",
    "headers": {"Authorization": "Bearer {api_key}"}
}
```

### 4. Улучшить CLI

Используй Rich для красивого вывода:

```python
from rich.panel import Panel
console.print(Panel("[green]Успех![/green]"))
```

## 🧪 Тестирование

```bash
# Запустить тесты
pytest

# Проверить самого себя
ai-review . --mode fast

# Проверить с verbose
ai-review . --mode fast --verbose
```

## 📋 Pull Request Process

1. Форкни репозиторий
2. Создай ветку: `git checkout -b feature/my-feature`
3. Закоммить: `git commit -am 'Add feature'`
4. Запушь: `git push origin feature/my-feature`
5. Открой PR

## 💡 Идеи для улучшения

- [ ] Поддержка Docker
- [ ] Web интерфейс
- [ ] VS Code extension
- [ ] GitHub App (PR comments)
- [ ] Плагинная система
- [ ] Больше языков (PHP, Ruby, Kotlin)
- [ ] Интеграция с GitLab CI
- [ ] Автофикс проблем

## 📜 License

MIT
