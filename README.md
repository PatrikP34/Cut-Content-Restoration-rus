Локальный скрипт для объединения существующего русского перевода **Fate/stay night REMASTERED** с ultimate edition (2004/PS2 Realta Nua) из проекта [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).

> [English version](README.md)

> Репозиторий не содержит оригинальную игру или игровые ресурсы. Получайте и используйте необходимые файлы только из установок и источников, к которым у вас есть законный доступ.

##  Сборка патча

### 1. Что потребуется

- **Fate/stay night REMASTERED** в Steam, версия `1.4.2.391`.
- Установленная **Fate/stay night [Réalta Nua] Ultimate Edition v1.1.4** — согласно требованиям [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).
- Следующие файлы и папка рядом с `build_russian_patch_latest.bat`:

| Файл или папка | Назначение |
|---|---|
| `russian_patch00m.bin` | Патч русского перевода patch00m.bin (чисто файл русского перевода от 31.07.2025) |
| `original_patch00m.bin` | Оригинальный файл patch00m.bin REMASTERED (исходник стимовского REMASTERED) |
| `restored_patch00m.en.bin` | Файл REMASTERED после обработки FSN-Remastered-Restoration |
| `decryptKey.bin` | Файл ключа расшифровки |
| `SomeKey.bin` | Дополнительный файл ключа |
| `main.exe` | Инструмент обработки EPK |
| `russian_merge/` | Скрипты сборки и вспомогательный код |

### 2. Найдите исходные файлы

Запустите `FSN.Restoration.Launcher.exe`. Файл REMASTERED после обработки FSN-Remastered-Restoration будет расположен в:

```text
%LOCALAPPDATA%\FSNRestoration\cache\patch00m.en.bin
```

Скопируйте этот файл в каталог сборки и переименуйте его в `restored_patch00m.en.bin`.

Оригинальный файл REMASTERED хранится здесь:

```text
%LOCALAPPDATA%\FSNRestoration\backup-obb\patch00m.bin
```

Скопируйте `patch00m.bin` в каталог сборки и переименуйте в `original_patch00m.bin` Обычно `%LOCALAPPDATA%` соответствует пути `C:\Users\<имя_пользователя>\AppData\Local`.

### 3. Запустите сборку

**Вариант A — через BAT-файл**

Запустите `build_russian_patch_latest.bat` и дождитесь завершения сборки.

**Вариант B — через командную строку PowerShell**

Находясь в каталоге проекта, выполните:

```powershell
.\build_russian_patch.bat --russian .\russian_patch00m.bin --baseline .\original_patch00m.bin --restored-english .\restored_patch00m.en.bin --fpd-key .\decryptKey.bin --some-key .\SomeKey.bin --epk-tool .\main.exe --output .\patch00m.ru.bin
```

### 4. Установите
После успешной сборки появится файл:

```text
patch00m.ru.bin
```

1. Переименуйте его в `patch00m.bin`.
2. Откройте каталог игры `Blade\obb`.
3. Сохраните резервную копию оригинального файла и замените его новым `patch00m.bin`.
4. Из русификатора скопируйте boot.dat (в настройках игры выберите English)

## Готовые файлы

(https://drive.google.com/drive/folders/188X3UV13WBZ7Ua07XgOgCZ83zMbu_71n?usp=drive_link) 

Требования к восстановлению и дополнительную информацию см. в проекте [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).

---

## (Credits)

### Оригинальная игра

- **TYPE-MOON** — *Fate/stay night*. Поддерживайте официальный релиз.
- **Команда Fate/stay night [Réalta Nua] Ultimate Edition** — Jacktheinfinite101, Quibi, Kotonoha и все участники, указанные в README проекта.
- **Mirror Moon** — английский перевод, использованный для восстановления строк.
- **Художники, выполнявшие демозаизацию изображений** — Bellandy и другие авторы, указанные в материалах Ultimate Edition.
- **[kurikomoe/FSNr_tools](https://github.com/kurikomoe/FSNr_tools)** — исследования форматов REMASTERED-пакетов и EPK, а также работы, связанные с расшифровкой. `fsnr/fpd.py` и `fsnr/epk.py` основаны на этой работе. Подробности — в [`THIRD_PARTY.md`](THIRD_PARTY.md).
- **[DaZombieKiller/FatePackageManager](https://github.com/DaZombieKiller/FatePackageManager)** — исследование формата игровых пакетов.
- https://github.com/morluto/rea

### Русский перевод — Русь-moon

- **Zanoru** — техническая часть, редактура и адаптация.
- **Shoule** — редактура и переработка графики.
- **Русь-мун** — предоставление текста и перевод.
- **Animevod** — сверка с японским оригиналом.
- **ausmood** — первоначальная помощь с текстурами.

### Использование ИИ

сприпт на основе лаунчера разработан при помощи AI coding agent Copilot gpt astra и REA: Reverse Engineer Anything

---

## License)

Код репозитория распространяется под лицензией **MIT**. Полный текст находится в [`LICENSE`](LICENSE). Информация о сторонних разработках и соответствующие уведомления приведены в [`THIRD_PARTY.md`](THIRD_PARTY.md).

**Fate/stay night и все игровые материалы принадлежат TYPE-MOON.** Это неофициальный фанатский проект, не связанный с TYPE-MOON, Aniplex или командой Ultimate Edition. Лицензия MIT распространяется только на код репозитория и не предоставляет прав на игру или её ресурсы.
