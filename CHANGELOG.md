# Changelog

## Unreleased
- Added the 2026-11-27 additional checks record (ja/en): server-side copy from volume to bucket, copies over 5 GiB, use alongside NFS, and splitting access points. Removed the process notes and open-item lists from the records, runbook, and docs.

- Initial scaffold: repository layout, gates (pins, naming, public safety, ja/en parity, matrix, make targets), CI, templates, and candidate-only pattern stubs.
- Reframed the references: the Playbook is the entry point and holds specifications and limits (pinned by commit SHA), and Serverless-Patterns is a sibling Spoke (pinned by release tag). Renamed `docs/hub-pin.md` to `docs/reference-pins.md`, the `drift-hub` target to `drift-pins`, and the Hub drafts to `drafts/playbook-pr/` and `drafts/playbook-feedback/`.
- Added `docs/use-cases` and `docs/integrations-map` (ja/en), an architecture figure with its generator and font/flow gates, `llms.txt`, and refreshed the README entry points.
