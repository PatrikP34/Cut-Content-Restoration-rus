# Third-party notices

This file records attribution and provenance information for external projects and materials referenced by or used in this repository. These notices do not grant additional rights to third-party software, code, translations, or game content.

## `kurikomoe/FSNr_tools`

Repository: <https://github.com/kurikomoe/FSNr_tools>

- `fsnr/fpd.py`: the FPD (`obb/*.bin`) reader follows `scripts/dec.py` from FSNr_tools. Its 56-byte header, big-endian entry table, and XOR stream are based on the format research documented there.
- `fsnr/epk.py`: a Python port of the `.epk` cipher from FSNr_tools `main.cpp` / `include/*.h`. The cipher is a Blowfish variant with a custom P-array; the S-boxes come from the game executable, and each file is keyed by its own name.
- `fsnr/keys.py`: downloads `scripts/decryptKey.bin` from FSNr_tools at commit `30c277be34c4a68aff9a7c2602579af7d118d259` and verifies it by SHA-256.

At the time of writing, no license file was identified in FSNr_tools. Attribution is not a substitute for a license or permission. Before redistributing or reusing derived portions, check the upstream repository's current terms and obtain permission from the author where necessary.

## `DaZombieKiller/FatePackageManager`

Repository: <https://github.com/DaZombieKiller/FatePackageManager>

Credited for research into the game's package format. This credit does not imply that its code is included in this repository.

## Fate/stay night [Réalta Nua] Ultimate Edition

Project resources: <https://github.com/Take00C/FSN-Remastered-Restoration>

The patch builder expects resources from the user's own installed copy at build time. The Ultimate Edition game files are not intended to be included in this repository.

## TYPE-MOON — Fate/stay night

*Fate/stay night* and all related game content, including text, images, audio, and other assets, are the property of TYPE-MOON and/or their respective rights holders. The MIT License for this repository does not cover those materials.

## Translation and restoration credits

- **Mirror Moon** — English translation used for restored lines.
- **Fate/stay night [Réalta Nua] Ultimate Edition team** — Jacktheinfinite101, Quibi, Kotonoha, and contributors credited in that project's README.
- **Fan demosaic artists** — Bellandy and other artists credited by the Ultimate Edition project.
- **Русь-moon** — Russian translation contributors: Zanoru, Shoule, Русь-мун, Animevod, and ausmood, as listed in `README.md`.

## AI-assisted development disclosure

The launcher was developed with assistance from Claude Code (Claude Opus 5.5, Anthropic), under the direction of the project maintainer.
