# Fate/stay night REMASTERED — Russian Patch Restoration

A local tool for combining an existing Russian translation of **Fate/stay night REMASTERED** with restored content from [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).

> [Русская версия документации](README.ru.md)

This repository does **not** include the original game or game assets. You must obtain and use the required files from installations and sources you are legally entitled to access.

## 📦 Build the patch

### 1. Requirements

- **Fate/stay night REMASTERED** on Steam, version `1.4.2.391`.
- **Fate/stay night [Réalta Nua] Ultimate Edition v1.1.4**, installed as required by [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).
- The files listed below in the same directory as `build_russian_patch_latest.bat`:

| File or directory | Purpose |
|---|---|
| `russian_patch00m.bin` | Source Russian translation patch |
| `original_patch00m.bin` | Original English REMASTERED patch |
| `restored_patch00m.en.bin` | English patch produced by FSN-Remastered-Restoration |
| `decryptKey.bin` | Decryption key file |
| `SomeKey.bin` | Additional key file |
| `main.exe` | EPK processing tool |
| `russian_merge/` | Build scripts and supporting code |

### 2. Locate the source patch files

Run `FSN.Restoration.Launcher.exe` to generate the restored English patch. The launcher stores it in the cache directory:

```text
%LOCALAPPDATA%\FSNRestoration\cache\patch00m.en.bin
```

Copy that file into the build directory and rename it to `restored_patch00m.en.bin`.

The original English patch is stored in:

```text
%LOCALAPPDATA%\FSNRestoration\backup-obb\original_patch00m.bin
```

Copy `original_patch00m.bin` into the build directory as well. `%LOCALAPPDATA%` usually expands to `C:\Users\<username>\AppData\Local`.

### 3. Run the build

**Option A — batch file**

Run `build_russian_patch_latest.bat` and wait for the build to finish.

**Option B — command line**

From the project directory, run:

```powershell
.\build_russian_patch.bat --russian .\russian_patch00m.bin --baseline .\original_patch00m.bin --restored-english .\restored_patch00m.en.bin --fpd-key .\decryptKey.bin --some-key .\SomeKey.bin --epk-tool .\main.exe --output .\patch00m.ru.bin
```

The command-line example uses `build_russian_patch.bat`; use the script names present in your checkout.

### 4. Install the result

After a successful build, the output file will be:

```text
patch00m.ru.bin
```

1. Rename it to `patch00m.bin`.
2. Open the game's `Blade\obb` directory.
3. Back up the original file, then replace it with the newly built `patch00m.bin`.

## 📥 Prebuilt files

A project-maintainer-provided [Google Drive folder](https://drive.google.com/drive/folders/188X3UV13WBZ7Ua07XgOgCZ83zMbu_71n?usp=drive_link) may contain the required and prebuilt files. Verify the contents and make sure you have the right to use any downloaded material.

For the restoration project and its requirements, see [FSN-Remastered-Restoration](https://github.com/Take00C/FSN-Remastered-Restoration).

---

## 🙏 Credits

### Original game and translation resources

- **TYPE-MOON** — *Fate/stay night*. Please support the official release.
- **Fate/stay night [Réalta Nua] Ultimate Edition team** — Jacktheinfinite101, Quibi, Kotonoha, and everyone credited in the project's README.
- **Mirror Moon** — English translation used for restored lines.
- **Fan demosaic artists** — Bellandy and the other artists credited by the Ultimate Edition project.

### Technical references and tools

- **[kurikomoe/FSNr_tools](https://github.com/kurikomoe/FSNr_tools)** — research into REMASTERED pack and EPK formats and related decryption work. `fsnr/fpd.py` and `fsnr/epk.py` are based on this work; see [`THIRD_PARTY.md`](THIRD_PARTY.md) for details.
- **[DaZombieKiller/FatePackageManager](https://github.com/DaZombieKiller/FatePackageManager)** — pack-format research.

### Russian translation — Русь-moon

- **Zanoru** — technical work, editing, and adaptation.
- **Shoule** — editing and graphics rework.
- **Русь-мун** — providing the text and translation.
- **Animevod** — checking against the Japanese original.
- **ausmood** — initial help with textures.

### AI disclosure

The launcher was developed with assistance from the AI coding agent **Claude Code (Claude Opus 5.5, Anthropic)** under the direction of the project maintainer.

---

## 📄 License

The repository code is released under the **MIT License**. See [`LICENSE`](LICENSE) for the license text and [`THIRD_PARTY.md`](THIRD_PARTY.md) for notices about work by other authors.

**Fate/stay night and all game content belong to TYPE-MOON.** This is an unofficial community project and is not affiliated with TYPE-MOON, Aniplex, or the Ultimate Edition team. The MIT License applies to the repository code only; it does not grant rights to the game or its assets.
