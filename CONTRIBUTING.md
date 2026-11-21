# Contributing / コントリビュート

## 日本語

1. 着手前に [AGENTS.md](AGENTS.md) を読みます。
2. ブランチは `feat/<短い説明>` または `docs/<短い説明>`、PR タイトルは `feat:`、`fix:`、`docs:`、`bench:`、`chore:`、`refactor:`、`test:`、`ci:`、`perf:`、`style:` のいずれかで始めます。
3. `make all` を通してから PR を出します。ゲートを触ったときは、失敗する入力のテストを足します。
4. 日本語版と英語版（`X.md` と `X.en.md`）を一緒に更新します。
5. 顧客名、個人名、アカウント ID、リソース ID、実際のアクセスポイント別名、サポートケース番号を書きません。
6. 数値は、環境と測定記録がそろっているものだけを書きます。未確認の項目は `candidate` のままにします。

## English

1. Read [AGENTS.md](AGENTS.md) before you start.
2. Name branches `feat/<short-description>` or `docs/<short-description>`, and start PR titles with `feat:`, `fix:`, `docs:`, `bench:`, `chore:`, `refactor:`, `test:`, `ci:`, `perf:`, or `style:`.
3. Run `make all` before opening a PR. When you change a gate, add a test with an input it must reject.
4. Update the Japanese and English versions (`X.md` and `X.en.md`) together.
5. Do not write customer names, personal names, account IDs, resource IDs, real access point aliases, or support case numbers.
6. Write a number only when its environment and measurement record exist. Leave unconfirmed items as `candidate`.
