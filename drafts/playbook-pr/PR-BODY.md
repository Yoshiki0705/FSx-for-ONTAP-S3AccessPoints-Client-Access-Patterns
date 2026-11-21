# Playbook PR 本文の下書き / Playbook PR body draft

> 下書きです。**提出しないでください。** Spoke の GitHub リポジトリが作られて公開されるまで、この PR は開けません。 / Draft. Do not open this PR until the Spoke repository exists and is public.

**タイトル案 / Title:** `docs: add Client Access Patterns Spoke to related repos`

**ブランチ名案 / Branch:** `docs/related-repos-client-access-patterns`

---

## Summary

Adds the FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns repository to the related-repositories tables (ja and en) and to the division-of-labour table in the citation index. The repository is a Spoke under the Playbook and a sibling of FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns. It holds client-tool setup steps, manual checklists, a compatibility matrix and measurement records for FSx for ONTAP S3 Access Points. It currently has no measurements.

**Do not merge or open before the Spoke repository exists and is public.** The README rows link to its URL, and `make cross-repo-external` looks the name up through the GitHub API.

## Changes

- `README.md`: one row in the related-repositories table.
- `docs/en/README.md`: one row in the English counterpart.
- `docs/ja/reference/cross-repo-index.md`: one row in `## 分担の原則`. The citation table is unchanged because the rows do not use `blob/` links.
- Optional, if the owner wants it: one bullet in the `llms.txt` sibling-repositories section. See the Spoke drafts for the text. Delete this line if it is not included.

The other six README languages (ko, zh-CN, zh-TW, fr, de, es) are not changed in this draft. Whether to add the row there, and who translates it, is left to the Playbook owner.

## Testing

- [ ] `make audit`, `make links`, `make cross-repo`, `make headings`, `make i18n-check`, `make switcher-check`, `make ja-markers` and `make anchors` pass in the PR worktree
- [ ] `make cross-repo-external` passes after the Spoke repository is public
- [ ] gitleaks clean
- [ ] Unit tests / cfn-lint: not applicable (documentation only)

## Blocked Features

- The six non-ja/en README languages are deferred.
- The Spoke repository must exist and be public before this PR is opened.
