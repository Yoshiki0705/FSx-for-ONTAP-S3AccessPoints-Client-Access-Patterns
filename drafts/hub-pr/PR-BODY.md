# Hub PR 本文の下書き / Hub PR body draft

> 下書きです。**提出しないでください。** Spoke の GitHub リポジトリが作られて公開されるまで、この PR は開けません（リンクが 404 になるため）。 / Draft. Do not open this PR until the Spoke repository exists and is public; the links would 404.

**タイトル案 / Title:** `docs: add client access patterns Spoke to related repositories`

**ブランチ名案 / Branch:** `docs/related-repos-client-access-patterns`

---

## Summary

Adds the FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns repository (the Spoke) to the related-repositories tables in `README.md` (ja) and `README.en.md`, and adds a Japanese/English page that states how the Hub and the Spoke divide the work.

**Do not merge or open before the Spoke repository exists and is public.** Its URL is linked from the README rows and the new page, and returns 404 until it is created.

## Changes

- `README.md`: one row in `### 関連リポジトリ`.
- `README.en.md`: one row in `### Related Repositories`.
- `docs/client-access-patterns-relation.md` and `docs/client-access-patterns-relation.en.md` (new): division of work, a Mermaid relationship diagram, and the flow of information (pinned release tag in, Issue / PR drafts out).
- Optional, one line each, if the owner wants them: a row in `docs/index.md` (`## 関連プロジェクト`) and a bullet in `llms.txt`. See the check results in the Spoke drafts. Delete this line if they are not included.

The other six README languages (de, es, fr, ko, zh-CN, zh-TW) are not changed. Whether to add the row there is left to the Hub owner.

## Testing

- [ ] `make drift` passes (includes `check_doc_pairs`, `check_i18n_parity`, `sync_lang_switcher --check`, `check_en_doc_language`, `check_neutral_wording`)
- [ ] `python3 tools/ai_style_rules.py . --summary --fail` passes for the new ja/en files
- [ ] Every link in the new files resolves on `main` (relative links) or, for the Spoke URL, after the repository is public
- [ ] gitleaks clean
- [ ] Unit tests / cfn-lint: not applicable (documentation only)

## Blocked Features

- The six non-ja/en README languages are deferred.
- The Spoke repository must exist and be public before this PR is opened.
