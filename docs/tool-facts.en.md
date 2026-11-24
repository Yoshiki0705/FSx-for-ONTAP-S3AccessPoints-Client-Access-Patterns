# Tool fact check

🌐 **Language**: [日本語](tool-facts.md) | **English**

> **Date and levels**: The check date is 2026-11-24 (Japan time). `D` in a table means I opened the official documentation or the official repository document and read that range. `C` means the documents are silent and nothing has been measured. No item here was confirmed on a real file system.

This page records what the official documents say about four tools (AWS CLI, s5cmd, rclone, Mountpoint for Amazon S3): the current version, the S3 APIs they use, and how to point them at S3 Access Points. The S3 operations that S3 Access Points support, and their limits, are in the [matrix cross-check](compatibility-matrix.en.md#s3-operations-used-by-the-tools-and-the-compatibility-list) and in the Playbook constraints note. They are not copied here.

## Scope of the check

- The four tools are the ones that stage 3 runs on a real file system (AWS CLI, s5cmd, rclone, Mountpoint for Amazon S3). For AWS Transfer Family only the facts were checked. For File Mover Express and the two LucidLink products, only the facts that go into the manual checklists were checked.
- Search-result snippets are not used as sources. Every URL in the tables is a page I opened and read.
- A version is what the official repository shows as the latest on the check date. Stage 3 records the version in use with `--version` at run time.

## Current versions and how to specify access points

| Tool | Latest version on the check date | Entry point for ordinary S3 operations | How to specify S3 Access Points | Sources |
|---|---|---|---|---|
| AWS CLI v2 | 2.42.2 (GitHub tag, commit date 2026-11-23 UTC). | `aws s3` (`cp`, `sync`, `ls`, `rm`) and `aws s3api` | An ARN can be written as `s3://arn:aws:s3:<region>:<account>:accesspoint/<name>/<key>` (`D`). An alias can be used in place of a bucket name (`D`). The alias of an FSx for ONTAP access point has the form `<name>-<metadata>-ext-s3alias` | S2, S6, S8 |
| s5cmd | v2.3.0 (released 2024-12-16, the latest GitHub shows) | `s5cmd cp`, `ls`, `sync`, `rm` | The README is silent (`C`). The README says a custom `--endpoint-url` falls back to path-style (`D`). S3 Access Points accept only virtual-hosted-style requests (`D`, S2), so whether an alias works together with `--endpoint-url` is unconfirmed | S2, S9, S10 |
| rclone | v1.76.0 (2026-11-06) | `rclone copy`, `ls`, `sync`, `mount` | The documents are silent (`C`). The default of `force_path_style` is `true` (`D`) and S3 Access Points accept only virtual-hosted-style requests (`D`, S2), so whether it must be set to `false` is unconfirmed | S2, S11, S12 |
| Mountpoint for Amazon S3 | 1.25.0 (2026-11-12) | `mount-s3 <bucket or access point> <mount point>` | Access points of S3 general purpose buckets and directory buckets can be given by ARN or alias (`D`). Whether an FSx for ONTAP access point can be given is not stated (`C`) | S13, S15, S16 |

## What is confirmed about the S3 APIs each tool uses

| Tool | API calls confirmed from the documents | Not confirmed from the documents |
|---|---|---|
| AWS CLI | An S3-to-S3 copy honors `--copy-props`, and a multipart copy may by default make extra `HeadObject`, `GetObjectTagging` and `PutObjectTagging` calls (`D`, S6). `--copy-props none` avoids the extra calls (`D`, S6). When `preferred_transfer_client` is `auto`, an S3-to-S3 copy does not use the CRT transfer client (`D`, S7) | Whether it issues `CopyObject` or `UploadPartCopy`, and at what size (`C`; check with `--debug`) |
| s5cmd | An S3-to-S3 copy runs on the server side (`D`, S9). Copying objects larger than 5 GB is not supported (`D`, S9). A listing first sends `ListObjects` (`D`, S9). `--use-list-objects-v1` switches to the V1 listing (`D`, S9) | The multipart upload, delete, and `HeadObject` calls (`C`) |
| rclone | A copy within one remote is a server-side copy (`D`, S11). Objects above `--s3-copy-cutoff` (default 4.656 GiB, maximum 5 GiB) are copied in chunks of that size (`D`, S11). The modification time is kept in `X-Amz-Meta-Mtime`, and reading it needs an extra `HEAD` (`D`, S11). Multipart or encrypted objects use `X-Amz-Meta-Md5chksum` (`D`, S11) | The listing API version, and when it uses `CopyObject` versus `UploadPartCopy` (`C`) |
| Mountpoint for Amazon S3 | Writing creates new files by default. Overwrite needs `--allow-overwrite` and delete needs `--allow-delete` (`D`, S14). Rename and append apply only to S3 Express One Zone (`D`, S14). Creating a directory is a local-only operation (`D`, S14) | Which APIs it calls at start-up and per operation against an FSx for ONTAP access point (`C`) |

## Facts confirmed for the other tools

| Tool | Confirmed fact | Source |
|---|---|---|
| AWS Transfer Family | FSx for ONTAP is used through S3 Access Points. Only aliases work; ARNs and virtual-hosted-style URIs do not. Rename and append are unsupported. Requests from Transfer Family are denied when the access point has a VPC network origin. IAM policy resources use the ARN, not the alias | S17 |
| File Mover Express | An open-source tool published by AWS (awslabs). The configuration holds a bucket name, a Region and a profile, and the network section has a field for an "S3 Access Point/VPC Endpoint" address. Whether an FSx for ONTAP access point alias can be given is not stated | S18 |
| LucidLink Connect | A data store holds a bucket name, access key, secret key, Region, endpoint, and a virtual-hosted-style flag. The documents say only `GetObject` permission is needed. Whether an FSx for ONTAP access point alias can be given is not stated | S19 |

## What could not be confirmed

1. Whether s5cmd and rclone accept an FSx for ONTAP access point alias.
2. Whether Mountpoint for Amazon S3 can mount an FSx for ONTAP access point alias. The Mountpoint README says it does not support S3-compatible storage other than Amazon S3 (S16). An FSx for ONTAP access point is an AWS S3 endpoint, but it cannot be read from the README whether that README covers it.
3. Whether each tool issues `CopyObject` or `UploadPartCopy` for a server-side copy ([server-side copy](server-side-copy.en.md)).
4. Whether File Mover Express and the two LucidLink products accept an FSx for ONTAP access point alias. The official documents are silent, so this stays in the checklist that the user fills in by hand.

## List of sources

All check dates are 2026-11-24 (Japan time).

| ID | Source | URL |
|---|---|---|
| S1 | FSx for ONTAP User Guide: Access point compatibility | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html |
| S2 | FSx for ONTAP User Guide: Referencing access points | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html |
| S3 | FSx for ONTAP User Guide: Configuring network access | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/configuring-network-access-for-s3-access-points.html |
| S4 | FSx for ONTAP User Guide: Managing access point access | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html |
| S5 | What's New (2026-11, server-side copy with S3 Access Points) | https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/ |
| S6 | AWS CLI reference: `aws s3 cp` | https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html |
| S7 | AWS CLI S3 configuration | https://docs.aws.amazon.com/cli/latest/topic/s3-config.html |
| S8 | AWS CLI tags (GitHub) | https://github.com/aws/aws-cli/tags |
| S9 | s5cmd README | https://github.com/peak/s5cmd/blob/master/README.md |
| S10 | s5cmd releases | https://github.com/peak/s5cmd/releases |
| S11 | rclone S3 documentation | https://rclone.org/s3/ |
| S12 | rclone releases | https://github.com/rclone/rclone/releases |
| S13 | Mountpoint configuration (CONFIGURATION.md) | https://github.com/awslabs/mountpoint-s3/blob/main/doc/CONFIGURATION.md |
| S14 | Mountpoint file behavior (SEMANTICS.md) | https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md |
| S15 | Mountpoint changelog | https://github.com/awslabs/mountpoint-s3/blob/main/mountpoint-s3/CHANGELOG.md |
| S16 | Mountpoint README | https://github.com/awslabs/mountpoint-s3/blob/main/README.md |
| S17 | Transfer Family User Guide: FSx for NetApp ONTAP | https://docs.aws.amazon.com/transfer/latest/userguide/fsx-s3-access-points.html |
| S18 | File Mover Express: Configuration | https://awslabs.github.io/filemoverexpress/docs/Configuration |
| S19 | LucidLink Connect Overview | https://developer.lucidlink.com/docs/connect/overview |
| S20 | FSx for ONTAP pricing | https://aws.amazon.com/fsx/netapp-ontap/pricing/ |
