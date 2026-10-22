Как запустить сборку

Убедитесь, что в папке рядом с build_russian_patch_latest.bat есть:

russian_patch00m.bin — файл исходного русского перевод;

original_patch00m.bin — файл оригинала английской версии Fate/stay night REMASTERED;

restored_patch00m.en.bin — файл, полученный после применения к нему патча https://github.com/Take00C/FSN-Remastered-Restoration;

decryptKey.bin и SomeKey.bin, main.exe;
папка russian_merge со скриптами сборщика.

FSN.Restoration.Launcher.exe создает restored_patch00m.en.bin в папке 
C:\users\<username>\AppData\Local\FSNRestoration\cache\patch00m.en.bin,

В C:\Users\<username>\AppData\Local\FSNRestoration\backup-obb хранится original_patch00m.bin 

Для объединения русификатора и патча Remastered-Restoration запустите build_russian_patch_latest.bat

либо через командую строку

.\build_russian_patch.bat --russian .\russian_patch00m.bin --baseline .\original_patch00m.bin --restored-english .\restored_patch00m.en.bin --fpd-key .\decryptKey.bin --some-key .\SomeKey.bin --epk-tool .\main.exe --output .\patch00m.ru.bin

После выполнения скрипта создается patch00m.ru.bin, переименуйте в patch00m.bin и поместите в Blade\obb c заменой

https://github.com/Take00C/FSN-Remastered-Restoration
What you need
Fate/stay night REMASTERED on Steam (game version 1.4.2.391).
Fate/stay night [Réalta Nua] Ultimate Edition v1.1.4, installed. You can install it from sukebei.nyaa. Claude made it mandatory cause of it's safety protections regarding redistributing copy right material and I don't know how to bypass pass it sadly. However, the only files you require from the Réalta Nua Ultimate Edition v1.1.4 is patch.xp3, patch_h.xp3, patch_hd_1920.xp3, patch_lang_english.xp3 and 6 more files as fall backs image.xp3, bgimage.xp3, fgimage.xp3, voice.xp3, sound.xp3, bgm.xp3 but the build never uses them. After that you should be good to go.

Или просто скачать все файлы, включая пропатченные
https://drive.google.com/drive/folders/188X3UV13WBZ7Ua07XgOgCZ83zMbu_71n?usp=drive_link

Credits

TYPE-MOON: Fate/stay night. Please support the official release.

The Fate/stay night [Réalta Nua] Ultimate Edition team: Jacktheinfinite101, Quibi, Kotonoha and everyone credited in their readme.

Mirror Moon: the English translation used for restored lines.

Fan demosaic artists: Bellandy and the others credited by the Ultimate Edition.

kurikomoe/FSNr_tools: the REMASTERED pack and epk formats and the decryption keys. fsnr/fpd.py and fsnr/epk.py are based on that work.

DaZombieKiller/FatePackageManager: pack format research.

AI disclosure: this launcher was built by an AI coding agent, Claude Code (Claude Opus 5.5, Anthropic), working with and directed by the publisher.

Русь-moon: Принимавшие участие Zanoru — Техническая часть, редактура и адаптация; Shoule — Редактура и переделка графики; Русь-мун — Предоставление текста и перевод; Animevod — Сверка с Японского; ausmood — Начальная помощь в текстурах;



License
The code is released under the MIT License (see LICENSE). See THIRD_PARTY.md for the parts based on other people's work. Fate/stay night and all game content belong to TYPE-MOON. This project is unofficial and not affiliated with TYPE-MOON,
Aniplex or the Ultimate Edition team.
