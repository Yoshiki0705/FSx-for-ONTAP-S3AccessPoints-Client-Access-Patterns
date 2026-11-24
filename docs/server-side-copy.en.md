# Server-side copy and client tools

🌐 **Language**: [日本語](server-side-copy.md) | **English**

> **Level**: This page holds only a reading of the official documents and the stage 3 verification steps. Until a tool is run on a real file system, whether it issues `CopyObject` or `UploadPartCopy` stays `C` (not measured).

In 2026-11, S3 Access Points made it possible to copy on the server side, with `CopyObject` and `UploadPartCopy`, between Amazon S3 general purpose buckets and FSx for ONTAP volumes within one Region ([What's New](https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/), read on 2026-11-24). Before that, server-side copy was unavailable, and each object had to be downloaded and uploaded again. This page sorts out whether each client tool uses the new path or falls back to download and upload.

## Split of responsibility with the Playbook

| Topic | Where it lives | Content |
|---|---|---|
| Whether the API works, and its constraints (copy combinations, SSE-FSX encryption, the `FSX_ONTAP` storage class, per-API measurements) | Playbook | The matching section of the constraints note. This repository does not link to it until that section is in the pinned commit |
| Which tool issues a server-side copy, and with which arguments | This repository | The table below and the stage 3 verification steps |
| Hands-on checks of general file-level and block-level copy and migration tools (DataSync, rsync, robocopy, XCP and others) | A Playbook issue (hands-on checks of copy and migration tools) | Not covered here |

The boundary is the path. The Playbook issue covers tools that go through NFS, SMB or iSCSI. This repository covers only client tools that reach S3 Access Points over the S3 API (AWS CLI, s5cmd, rclone, Mountpoint for Amazon S3 and similar).

## Expected behavior per tool

| Tool | Arguments that should trigger a server-side copy | Expectation from the documents | How to judge | Level |
|---|---|---|---|---|
| AWS CLI | `aws s3 cp s3://<bucket>/<key> s3://<alias>/<key>` | Handled as an S3-to-S3 copy. A multipart copy may make extra `HeadObject`, `GetObjectTagging` and `PutObjectTagging` calls | Look for `CopyObject` or `UploadPartCopy` in the `--debug` output. Also compare with `--copy-props none` | `C` |
| s5cmd | `s5cmd cp s3://<bucket>/<key> s3://<alias>/<key>` | The README calls an S3-to-S3 copy server-side. It says objects larger than 5 GB are unsupported | Compare the client's sent and received bytes before and after the same copy. Check the CloudTrail data events | `C` |
| rclone | `rclone copy <remote>:<bucket> <remote>:<alias>` within one remote | A copy within one remote is a server-side copy (official documentation). Above `--s3-copy-cutoff` it copies in chunks | Look for the `x-amz-copy-source` header with `-vv --dump headers` | `C` |
| Mountpoint for Amazon S3 | None | The documents give no argument that triggers a server-side copy. A `cp` between two mounts is expected to read and then write (unconfirmed). Rename applies only to S3 Express One Zone | `cp` from one mount to another access point and check that the sent and received bytes are close to the object size | `C` |

## How stage 3 verifies

Stage 3 checks which API was issued with three independent pieces of evidence. No single one decides the result.

1. The client's debug output: `--debug` for AWS CLI, `-vv --dump headers` for rclone.
2. The client's sent and received bytes: take the difference of `/proc/net/dev` before and after the copy. A server-side copy of a 256 MiB object should leave a difference far smaller than the object size. A download plus upload pushes the difference toward twice the size.
3. CloudTrail data events (optional): read the `eventName` of `CopyObject` and `UploadPartCopy`. This needs a dedicated trail, so it is an approval item in the runbook. The scripts do not include it; create the trail by hand after approval.

As a control that should succeed, first copy the same object directly with `aws s3api copy-object` and confirm that the first and second pieces of evidence show the shape of a server-side copy.

```bash
benchmarks/scripts/stage3-measure.sh --dry-run --case server-side-copy
```

## What is not confirmed

- Whether each tool issues `CopyObject` or `UploadPartCopy`, and at what size.
- Whether the Playbook's per-API measurements can be read as results for client tools. Per-tool results are measured in stage 3 of this repository.
- A reference to the matching Playbook section. It is added with the follow-up procedure in [docs/reference-pins.md](reference-pins.md) once that section is in the pinned commit.
