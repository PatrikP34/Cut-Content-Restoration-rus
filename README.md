Как запустить сборку
Убедитесь, что в папке рядом с build_russian_patch.bat есть:

russian_patch00m.bin — исходный русский архив;
original_patch00m.bin — чистый английский архив до Restoration;
restored_patch00m.en.bin — английский архив после подготовки Restoration;
decryptKey.bin и SomeKey.bin;
main.exe;
папка russian_merge со скриптами сборщика.
Откройте эту папку в Проводнике. Кликните по адресной строке, введите powershell и нажмите Enter.


.\build_russian_patch.bat --russian .\russian_patch00m.bin --baseline .\original_patch00m.bin --restored-english .\restored_patch00m.en.bin --fpd-key .\decryptKey.bin --some-key .\SomeKey.bin --epk-tool .\main.exe --output .\patch00m.ru.bin


https://github.com/Take00C/FSN-Remastered-Restoration
What you need
Fate/stay night REMASTERED on Steam (game version 1.4.2.391).
Fate/stay night [Réalta Nua] Ultimate Edition v1.1.4, installed. You can install it from sukebei.nyaa. Claude made it mandatory cause of it's safety protections regarding redistributing copy right material and I don't know how to bypass pass it sadly. However, the only files you require from the Réalta Nua Ultimate Edition v1.1.4 is patch.xp3, patch_h.xp3, patch_hd_1920.xp3, patch_lang_english.xp3 and 6 more files as fall backs image.xp3, bgimage.xp3, fgimage.xp3, voice.xp3, sound.xp3, bgm.xp3 but the build never uses them. After that you should be good to go.
