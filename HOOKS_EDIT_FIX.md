# Исправление: Редактирование хуков не сохраняется

## Проблема

Когда пользователь редактировал хук и изменял его имя, изменения не сохранялись корректно в `.claude/settings.json`.

### Причина

При обновлении хука код пытался удалить старую конфигурацию из `settings.json`, используя **новое имя** хука (после обновления). Это приводило к тому, что:

1. Старая конфигурация оставалась в `settings.json` под старым именем
2. Новая конфигурация добавлялась под новым именем
3. В итоге в `settings.json` было 2 копии хука с разными именами

### До исправления

```python
# ❌ НЕПРАВИЛЬНО
custom_hook.name = hook_update.name  # Обновили имя

# Пытаемся удалить старую конфигурацию, но используем НОВОЕ имя
await self.file_service.remove_hook_from_settings(
    project_path=project.path,
    hook_name=custom_hook.name  # <- Это уже новое имя!
)
```

## Решение

Сохраняем старое имя хука **ДО** обновления, чтобы правильно удалить его из `settings.json`.

### После исправления

```python
# ✅ ПРАВИЛЬНО
# Сохраняем старое имя
old_hook_name = custom_hook.name

# Обновляем хук с новым именем
custom_hook.name = hook_update.name
custom_hook.description = hook_update.description
# ... другие поля

# Удаляем старую конфигурацию используя СТАРОЕ имя
await self.file_service.remove_hook_from_settings(
    project_path=project.path,
    hook_name=old_hook_name  # <- Используем сохраненное старое имя
)

# Добавляем новую конфигурацию с НОВЫМ именем
await self.file_service.apply_hook_to_settings(
    project_path=project.path,
    hook_name=custom_hook.name,  # <- Новое имя
    hook_config=custom_hook.hook_config
)
```

## Файлы изменены

**`claudetask/backend/app/services/hook_service.py`**

### 1. Custom hooks (строки 435-473)
```python
if custom_hook:
    # Save old name for settings.json cleanup
    old_hook_name = custom_hook.name  # ← ДОБАВЛЕНО
    
    # Update custom hook
    custom_hook.name = hook_update.name
    # ... обновление других полей
    
    # If enabled, update settings.json
    if project_hook:
        # Remove old config using OLD name
        await self.file_service.remove_hook_from_settings(
            project_path=project.path,
            hook_name=old_hook_name  # ← ИЗМЕНЕНО: было custom_hook.name
        )
        
        # Apply new config using NEW name
        await self.file_service.apply_hook_to_settings(
            project_path=project.path,
            hook_name=custom_hook.name,
            hook_config=custom_hook.hook_config
        )
```

### 2. Default hooks (строки 488-526)
```python
if default_hook:
    # Save old name for settings.json cleanup
    old_hook_name = default_hook.name  # ← ДОБАВЛЕНО
    
    # Update default hook
    default_hook.name = hook_update.name
    # ... обновление других полей
    
    # If enabled, update settings.json
    if project_hook:
        # Remove old config using OLD name
        await self.file_service.remove_hook_from_settings(
            project_path=project.path,
            hook_name=old_hook_name  # ← ИЗМЕНЕНО: было default_hook.name
        )
        
        # Apply new config using NEW name
        await self.file_service.apply_hook_to_settings(
            project_path=project.path,
            hook_name=default_hook.name,
            hook_config=default_hook.hook_config
        )
```

## Тестирование

### Тест 1: Обновление имени хука
```bash
# 1. Создать custom hook с именем "My Hook"
# 2. Включить хук
# 3. Проверить .claude/settings.json - должен быть "My Hook"
# 4. Отредактировать хук, изменить имя на "My Updated Hook"
# 5. Проверить .claude/settings.json:
#    ✅ НЕТ конфигурации "My Hook"
#    ✅ ЕСТЬ конфигурация "My Updated Hook"
```

### Тест 2: Обновление без изменения имени
```bash
# 1. Создать хук с именем "Test Hook"
# 2. Включить хук
# 3. Отредактировать описание (имя НЕ менять)
# 4. Проверить .claude/settings.json:
#    ✅ Конфигурация "Test Hook" обновлена
#    ✅ НЕТ дубликатов
```

### Тест 3: Обновление отключенного хука
```bash
# 1. Создать хук (НЕ включать)
# 2. Отредактировать хук, изменить имя
# 3. Проверить .claude/settings.json:
#    ✅ Файл НЕ изменился (хук не был включен)
# 4. Включить хук
# 5. Проверить .claude/settings.json:
#    ✅ Добавлена конфигурация с НОВЫМ именем
```

## Результат

✅ **Исправлено:** Теперь при редактировании хука с изменением имени:
1. Старая конфигурация корректно удаляется из `settings.json`
2. Новая конфигурация добавляется с новым именем
3. Нет дубликатов в `settings.json`
4. Изменения сохраняются корректно в базе данных
5. Frontend отображает обновленные данные после refresh

✅ **Работает для:**
- Custom hooks
- Default hooks
- Enabled hooks
- Disabled hooks

---

**Дата исправления:** 2025-11-13  
**Затронутые файлы:** `claudetask/backend/app/services/hook_service.py`
