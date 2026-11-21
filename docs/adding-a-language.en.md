# Adding a language

The README and the main documents exist in Japanese and English. The Hub has 8 languages (ja, en, ko, zh-CN, zh-TW, fr, de, es), and naming follows it. The repository maintainer decides whether to add one.

## File naming

- Japanese is `X.md` and English is `X.en.md`.
- An added language is `X.<language code>.md` (for example `README.ko.md` and `README.zh-CN.md`).
- Use the same spelling of the language code as the Hub README.

## Steps to add a language

1. Create `X.<language code>.md` for every document. Match the Japanese version in the number and order of headings, the number of table columns, and the number of notes.
2. Add a link to the new language in the language switch line at the top of each README.
3. Extend `scripts/check_parity.py` to compare the new pairs. After extending it, confirm with a test in `make test` that it fails on an input missing one side.
4. Run `make all` until it passes.
5. Put the change in one commit.
