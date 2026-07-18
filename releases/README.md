# GitHub Releases — bilingual notes (EN / RU)

Release titles and bodies for [GitHub Releases](https://github.com/PyOrchestrator/PyOrchestrator/releases).

Each file: `vX.Y.Z.md` — used with `gh release create` / `gh release edit`.

```bash
# Title = first line; notes body = full file (or strip title with tail -n +3)
gh release edit v0.1.13 --title "$(head -1 releases/v0.1.13.md)" --notes-file releases/v0.1.13.md
```

## Bilingual format

Each `vX.Y.Z.md` starts with a one-line title, then `---`, then **English** and **Русский** sections.

**CHANGELOG.md** remains the full English history.
