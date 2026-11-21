# Security policy / セキュリティ方針

## 日本語

脆弱性や、リポジトリに混入した秘密情報（鍵、アカウント ID、実在のリソース ID など）を見つけたときは、公開の Issue に詳細を書かず、リポジトリの保守者に非公開で連絡してください（GitHub の Private vulnerability reporting を使えるときはそれを使います）。

秘密情報が公開済みの履歴に入った場合の対応:

1. 該当の鍵や認証情報を、先に無効化または削除する。
2. 履歴の書き換えが必要かを判断する。公開リポジトリの履歴は複製されうるため、無効化を優先する。
3. Hub の方針に合わせて、再発防止のゲートを足す。

## English

If you find a vulnerability, or a secret that slipped into the repository (a key, an account ID, a real resource ID), do not post details in a public issue. Contact the maintainer privately (use GitHub private vulnerability reporting when it is available).

When a secret has entered published history:

1. Revoke or delete the key or credential first.
2. Decide whether history must be rewritten. Published history can be copied, so revocation comes first.
3. Add a gate that prevents recurrence, consistent with the Hub's practice.
