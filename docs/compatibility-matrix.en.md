# Compatibility matrix

Confirmation status of the operations client tools perform against FSx for ONTAP S3 Access Points. Every cell is `candidate` (unconfirmed) and carries no numbers.

> **How to read it**: the mark at the start of a cell is the confirmation level. `C` is unconfirmed, `D` is confirmed in official documentation (URL and date), `M` is confirmed by running it (link to the record), and `-` is not applicable. Limits of S3 Access Points themselves are not written here; see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese).

## Legend

| Mark | Level | How to write the cell |
|---|---|---|
| `C` | `candidate` | Write `C` only. No numbers |
| `D` | `documented` | `D`, the official URL, and the date (YYYY-MM-DD) |
| `M` | `measured` | `M` and a link to the measurement or checklist record |

## Ingest and transfer tools

| Tool | List | Get | Put | Multipart | Delete | Mount behavior | Date | Pinned Playbook commit | Source |
|---|---|---|---|---|---|---|---|---|---|
| AWS CLI（version unconfirmed） | C | C | C | C | C | - | - | - | - |
| rclone（version unconfirmed） | C | C | C | C | C | - | - | - | - |
| s5cmd（version unconfirmed） | C | C | C | C | C | - | - | - | - |
| AWS Transfer Family（version unconfirmed） | C | C | C | C | C | - | - | - | - |
| File Mover Express（version unconfirmed） | C | C | C | C | C | - | - | - | - |

## Streaming and mount tools

| Tool | List | Get | Put | Multipart | Delete | Mount behavior | Date | Pinned Playbook commit | Source |
|---|---|---|---|---|---|---|---|---|---|
| Mountpoint for Amazon S3（version unconfirmed） | C | C | C | C | C | C | - | - | - |
| rclone mount（version unconfirmed） | C | C | C | C | C | C | - | - | - |
| LucidLink Connect（version unconfirmed） | C | C | C | C | C | C | - | - | - |
| LucidLink Suite（version unconfirmed） | C | C | C | C | C | C | - | - | - |

## Update procedure

1. Change the confirmed cell from `C` to `D` or `M`, and write the date and the pinned Playbook commit (first 12 hex digits of the SHA) in the same row.
2. Run `check_matrix` through `make drift`.
3. When the pinned Playbook commit changes, re-confirm the affected rows as `stale` ([docs/reference-pins.md](reference-pins.md)).
