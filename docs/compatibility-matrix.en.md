# Compatibility matrix

Confirmation status of the operations client tools perform against FSx for ONTAP S3 Access Points. Every cell is `candidate` (unconfirmed) and carries no numbers.

> **How to read it**: the mark at the start of a cell is the confirmation level. `C` is unconfirmed, `D` is confirmed in official documentation (URL and date), `M` is confirmed by running it (link to the record), and `-` is not applicable. Limits of S3 Access Points themselves are not written here; see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese).

## Legend

| Mark | Level | How to write the cell |
|---|---|---|
| `C` | `candidate` | Write `C` only. No numbers |
| `D` | `documented` | `D`, the official URL, and the date (YYYY-MM-DD) |
| `M` | `measured` | `M` and a link to the measurement or checklist record |

## Ingest and transfer tools

| Tool | List | Get | Put | Multipart | Delete | Mount behavior | Date | Pinned Playbook commit | Source |
|---|---|---|---|---|---|---|---|---|---|
| AWS CLI 2.38.0 | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |
| rclone v1.76.0 | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | C | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |
| s5cmd v2.3.0 | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | C | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |
| AWS Transfer Family（version unconfirmed） | C | C | C | C | C | - | - | - | - |
| File Mover Express（version unconfirmed） | C | C | C | C | C | - | - | - | - |

## Streaming and mount tools

| Tool | List | Get | Put | Multipart | Delete | Mount behavior | Date | Pinned Playbook commit | Source |
|---|---|---|---|---|---|---|---|---|---|
| Mountpoint for Amazon S3 1.24.0 | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | M [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) | 2026-11-24 | a4c8367f9172 | [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |
| rclone mount（version unconfirmed） | C | C | C | C | C | C | - | - | - |
| LucidLink Connect（version unconfirmed） | C | C | C | C | C | C | - | - | - |
| LucidLink Suite（version unconfirmed） | C | C | C | C | C | C | - | - | - |

## S3 operations used by the tools and the compatibility list

The second column is what the AWS compatibility list ([Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html), read on 2026-11-24) says. The tool columns record whether that tool issues the operation, and every cell is `C` (not measured). What could be read from the documents is in the [tool fact check](tool-facts.en.md).

| S3 operation | AWS compatibility list | AWS CLI | s5cmd | rclone | Mountpoint for Amazon S3 |
|---|---|---|---|---|---|
| ListObjectsV2 | Supported | M | C | C | M |
| GetObject and HeadObject | Supported | M | C | C | M |
| PutObject | Supported | M | C | M | M |
| Multipart (CreateMultipartUpload, UploadPart, CompleteMultipartUpload, AbortMultipartUpload) | Supported | M | C | C | M |
| CopyObject (same Region) | Supported | M | C | M | C |
| UploadPartCopy (same Region) | Supported | M | C | C | C |
| DeleteObject and DeleteObjects | Supported | C | C | C | M |
| GetObjectTagging and PutObjectTagging | Supported | M | C | C | C |
| HeadBucket and GetBucketLocation | Supported | C | C | C | C |
| Conditional writes (`If-None-Match`, `If-Match`) | Not supported | M | C | C | C |
| ListObjectVersions | Not supported | C | C | C | C |

> **How to read the cross-check**: If a tool issues an operation that the AWS list marks as not supported, that operation should fail. For example, the documents do not say how `aws s3 cp --no-overwrite` prevents an overwrite, and it can fail if it uses a conditional write. Stage 3 checks, tool by tool, whether the rows that the AWS list marks as not supported are issued.

> **Cells filled by measurement**: An `M` cell means the tool's debug log showed it issuing that operation ([2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md)). s5cmd stays `C` because its log shows no API names. AWS CLI sent `If-None-Match` with `aws s3 cp --no-overwrite`, and the access point returned `NotImplemented`.

## Update procedure

1. Change the confirmed cell from `C` to `D` or `M`, and write the date and the pinned Playbook commit (first 12 hex digits of the SHA) in the same row.
2. Run `check_matrix` through `make drift`.
3. When the pinned Playbook commit changes, re-confirm the affected rows as `stale` ([docs/reference-pins.md](reference-pins.md)).
