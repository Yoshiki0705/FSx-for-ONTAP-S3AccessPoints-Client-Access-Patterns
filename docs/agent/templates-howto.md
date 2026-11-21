# 雛形の使い方

雛形は `docs/templates/` にあり、日本語（`X.md`）と英語（`X.en.md`）が対になっています。

| 作るもの | 雛形 | 置き場所 |
|---|---|---|
| ツール 1 つのパターン | `pattern.md` / `pattern.en.md` | `patterns/<群>/<ツール>/README.md` と `README.en.md` |
| 商用ツールの手動チェックリスト | `checklist.md` / `checklist.en.md` | `checklists/vendor/<ツール>/CHECKLIST.md` と `CHECKLIST.en.md` |
| マトリクスの 1 行 | `matrix-row.md` / `matrix-row.en.md` | `docs/compatibility-matrix.md` と `.en.md` |
| ベンチマーク記録 | `benchmark-record.md` / `benchmark-record.en.md` | `benchmarks/records/<日付>-<ツール>-<シナリオ>.md` |

## 手順

1. 雛形をコピーし、`<tool>` を実際の名前に置き換える。
2. 確認できていない欄は「未記入」のままにする。もっともらしい既定値で埋めない。
3. 日本語版と英語版を同時に更新する。見出しの数と順序、表の列数、注記の数を揃える（`make drift` の `check_parity`）。
4. Playbook へのリンクは `docs/reference-pins.md` の固定コミットを使った `blob/<コミット SHA>/` の形、Serverless-Patterns へのリンクは固定タグを使った `blob/<タグ>/` の形で書く。
