# 2026-11-24 client tools on a real file system (stage 3)

🌐 **Language**: [日本語](2026-11-24-client-tools-stage3.md) | **English**

> **Class**: A sample run. Each operation ran once on one configuration, and only success or failure and a content-hash match were recorded. No performance numbers were recorded. IDs, the account ID and the access point alias are redacted.

## Environment

| Field | Value |
|---|---|
| benchmark_run_id | 20261124-1500 |
| Measured on | 2026-11-24 15:03 to 15:12 (Japan time) |
| Region | ap-northeast-1 |
| FSx for ONTAP layout | An existing verification file system (first generation `SINGLE_AZ_1`, throughput capacity 128 MBps, SSD 1,024 GiB). A 20 GiB UNIX security style volume was created only for this run and deleted at teardown |
| ONTAP version | 9.19.1P4 (read on the same file system on 2026-11-27; see the [additional checks record](2026-11-27-client-tools-additional.en.md)) |
| S3 Access Points settings | Network origin VPC. File system user UNIX `root`. No access point policy (allowed by an IAM role in the same account) |
| Client | EC2 c6in.xlarge, Amazon Linux 2023 (kernel 6.18). Same subnet as the file system. S3 reached through a gateway VPC endpoint |
| Tools and versions | AWS CLI 2.38.0 (bundled with the AMI), s5cmd 2.3.0, rclone 1.76.0, Mountpoint for Amazon S3 1.24.0 (installed with `dnf`) |
| Object size | 1 MiB, 64 MiB, 256 MiB (random) |
| Parallelism | Each tool's default |
| Repetitions and aggregation | Each operation once. No aggregation |
| Measurement class | Sample run |
| Result | The tables below: success or failure, errors, hash match. Server-side copy also records the client's sent and received bytes |
| Reproduction | The [stage 3 runbook](../stage3-runbook.en.md): `stage3-setup.sh`, `stage3-measure.sh --case <case>`, `stage3-export-evidence.sh`, `stage3-teardown.sh` |
| Cleanup | All five kinds of created resources (bucket, volume, access point, IAM role and instance profile, EC2) were deleted and read back with describe. See [cleanup results](#cleanup-results) |

## Control results

In the same run, the same operations also ran on an ordinary S3 general purpose bucket.

| Operation | Ordinary bucket | Access point (alias) | Access point (ARN) |
|---|---|---|---|
| `aws s3api list-objects-v2` | Succeeded | Succeeded | Succeeded |
| `put-object` (1 MiB), `head-object`, `get-object` | - | Succeeded. Hash matched. `StorageClass` was `FSX_ONTAP`, encryption `aws:fsx` | - |

## Results per tool

| Tool | Operation | Ordinary bucket | Access point |
|---|---|---|---|
| AWS CLI | `aws s3 ls`, `cp` (1 MiB and 64 MiB), `sync`, `rm` (both alias and ARN) | Succeeded | Succeeded. The 64 MiB hash matched. The 64 MiB file was sent as a multipart upload (8 parts) |
| AWS CLI | `aws s3 cp --no-overwrite` | Succeeded | Failed. `NotImplemented` (A header you provided implies functionality that is not implemented). `--debug` showed `If-None-Match: *` |
| s5cmd | `cp` (1 MiB and 64 MiB), download, `rm` (wildcard) | Succeeded | Succeeded. The 64 MiB hash matched. The alias was accepted without `--endpoint-url` |
| s5cmd | `ls` of an empty prefix | Exit code 1 (no object found) | Exit code 1 (the same) |
| rclone | `lsf`, `copyto`, download, `delete` (`force_path_style = false`) | Succeeded | Succeeded. The 64 MiB hash matched (a single `PutObject`) |
| rclone | `check` | 1 matching files | 0 differences, but 1 hashes could not be checked |
| Mountpoint for Amazon S3 | Mount by alias, mount by ARN | Succeeded | Succeeded |
| Mountpoint for Amazon S3 | Default flags: new write, read | Succeeded | Succeeded |
| Mountpoint for Amazon S3 | Default flags: overwrite, append, delete | Operation not permitted | Operation not permitted (the same) |
| Mountpoint for Amazon S3 | `--allow-overwrite --allow-delete`: overwrite, delete | Succeeded | Succeeded |
| Mountpoint for Amazon S3 | Rename | Function not implemented | Function not implemented (the same) |
| Mountpoint for Amazon S3 | `mkdir` and a write below it | Succeeded | Succeeded |

The Mountpoint debug log showed `ListObjectsV2`, `HeadObject`, `GetObject`, `PutObject`, `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload` and `DeleteObject` against the access point. The mount of the ordinary bucket showed the same kinds of API calls.

## Server-side copy results

A 256 MiB object was copied from the ordinary bucket to the access point alias. Sent and received bytes are the difference on the client's network interface before and after the copy (256 MiB = 268,435,456 bytes).

| Copy method | API issued (from the logs) | Sent and received bytes | Content hash |
|---|---|---|---|
| Control: `aws s3api copy-object` | `CopyObject` | 26,740 | Matched |
| `aws s3 cp` (default) | `HeadObject`, `GetObjectTagging`, `CreateMultipartUpload`, 32 `UploadPartCopy`, `CompleteMultipartUpload` | 236,963 | Matched |
| `aws s3 cp --copy-props none` | `HeadObject`, `CreateMultipartUpload`, 32 `UploadPartCopy`, `CompleteMultipartUpload` | 232,721 | Matched |
| `s5cmd cp` | No API names in the log | 27,340 | Matched |
| `rclone copyto` (default) | `CopyObject` sent with `X-Amz-Storage-Class: STANDARD`; failed 3 times with `InvalidStorageClass` | 82,198 | No destination object |
| `rclone copyto --s3-storage-class FSX_ONTAP` | `CopyObject` (`X-Amz-Storage-Class: FSX_ONTAP`) | 66,991 | Matched |
| Reference: download with `aws s3 cp` and upload from standard input | Download and upload | 551,933,428 | Matched |

Where the sent and received bytes are below 1 MB, the data did not pass through the client. The download-and-upload reference was about twice the object size. The s5cmd log shows no API names, so s5cmd was judged by bytes and hash only. CloudTrail data events were not used.

## Cleanup results

Before teardown, the client logs, hashes, byte counts and the describe output of each resource were moved to a private location (108 files). The redacted result tables (hashes, byte counts, exit codes per operation, tool versions, teardown read-back) are in [20261124-1500/](20261124-1500/). Teardown ran from 15:12 to 15:15 (Japan time), and each resource was read back with describe.

| Resource | Read-back |
|---|---|
| S3 Access Points | `NotFound` |
| Dedicated test volume | `VolumeNotFound` |
| EC2 | `terminated`. 0 attached EBS volumes |
| IAM role, instance profile | `NoSuchEntity` |
| S3 bucket | 404 |

A search by tag (`Project=client-access-patterns`) still showed one terminated EC2 instance. Terminated instances stay visible to tag search for a while. Running or stopped instances: 0.
