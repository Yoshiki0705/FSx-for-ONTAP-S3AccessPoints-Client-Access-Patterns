# Writing a matrix row

🌐 **Language**: [日本語](matrix-row.md) | **English**

A matrix row describes the confirmation status of one version of one tool. Levels and cell formats follow the legend in the [compatibility matrix](../compatibility-matrix.en.md).

## Example row

```text
| <tool> (<version>) | C | D <official URL> <YYYY-MM-DD> | M [record](<path to record>) | C | C | - | <YYYY-MM-DD> | <pinned Hub tag> | <source> |
```

## Required fields

| Item | Content |
|---|---|
| Level mark | One of `C`, `D`, `M`, `-` |
| Date | Required for a row that contains `D` or `M` |
| Pinned Hub tag | The value at the time of confirmation. A row that differs from the current pin counts as `stale` |
