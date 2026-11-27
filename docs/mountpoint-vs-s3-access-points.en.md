# Mountpoint for Amazon S3 and S3 Access Points: choosing between them

🌐 **Language**: [日本語](mountpoint-vs-s3-access-points.md) | **English**

> **Level**: The tables record what the official documents said when I read them on 2026-11-24. Source IDs are in the source list of the [tool fact check](tool-facts.en.md). Mountpoint for Amazon S3 has not yet been run against an FSx for ONTAP access point on a real file system. `C` means the documents are silent and nothing has been measured.

There are three ways to reach FSx for ONTAP data. This page lines up the constraints of the three paths on the same axes and gives pointers for choosing. Each path suits some situations and not others, and nothing here ranks them.

## The three paths compared

| Mark | Path | Entry point | Prerequisite on FSx for ONTAP |
|---|---|---|---|
| a | Mount an access point with Mountpoint for Amazon S3 | `mount-s3 <alias> <mount point>` | Whether Mountpoint accepts an FSx for ONTAP access point is not stated (`C`). The Mountpoint README says it does not support S3-compatible storage other than Amazon S3 (S16) |
| b | Reach the access point with a tool that uses the S3 API directly (AWS CLI, s5cmd, rclone) | `aws s3 ...`, `s5cmd ...`, `rclone ...` | An ARN or alias can be given. For AWS CLI this is documented (S6); for s5cmd and rclone the documents are silent (`C`) |
| c | Mount the FSx for ONTAP volume directly over NFS or SMB (for reference) | The OS `mount` | Attaching an access point does not change behavior over NFS and SMB (S4) |

## Constraints per axis

| Axis | a: Mountpoint | b: S3 API tools | c: NFS or SMB (reference) | Sources |
|---|---|---|---|---|
| Renaming a file | Does not emulate rename on S3 general purpose buckets. Rename applies only to S3 Express One Zone | The compatibility list for FSx for ONTAP access points has no operation that corresponds to rename (it is a partial list). The Transfer Family documentation says rename and append are unavailable | A file system operation that can be run (`C`: no source taken on this page) | S14, S17 |
| Append | Only S3 Express One Zone. Needs `--incremental-upload` | `PutObject` rewrites the whole object (general S3 API behavior, `C`) | A file system operation that can be run (`C`) | S14, S17 |
| Overwrite | By default only creates new files. Overwrite needs `--allow-overwrite` and a write that truncates | `PutObject` can write the same key. Conditional writes are unsupported | A file system operation that can be run (`C`) | S1, S14 |
| Directories | Inferred from `/` in keys. `mkdir` is a local-only operation. An existing directory can be neither removed nor renamed | Listed as key prefixes. How they map to real directories in the volume is `C` | Real directories can be created and removed (`C`) | S14 |
| Metadata | Does not emulate changing ownership or permissions. Modification time and size are limited and cannot be changed | Object metadata. Whether a file's UNIX owner and permissions show up as S3 metadata is `C` | Files carry an owner, permissions, and ACLs | S4, S14 |
| Where permissions are decided | S3 decides with the process's IAM credentials, then the permissions of the file system user set on the access point decide. Locally, by default only the user who mounted can read (`--allow-other` widens this) | Decided by IAM and the access point policy, then by the permissions of the file system user | The client's identity is judged by the volume's security style (UNIX mode bits or NFSv4 ACLs, NTFS ACLs) | S4, S14 |
| Network path | HTTPS to the S3 endpoint. For a VPC-origin access point, go through a VPC endpoint in the same VPC. An interface endpoint needs `--endpoint-url` | The same. Tools treat `--endpoint-url` differently (s5cmd falls back to path-style) | File protocols directly to the SVM endpoint (`C`: no source taken on this page) | S3, S9, S13 |
| Cache | Optional metadata and data caching exists. When enabled, the metadata time-to-live defaults to 1 minute. An object changed by another client can show stale metadata for up to 1 second by default | The tools keep no cache (`C`) | Follows the NFS and SMB client caches (`C`) | S14 |
| Suited to | Applications that read large objects at high throughput. Writing new files sequentially from one client | Bulk copy, sync, batch jobs. Server-side copy ([server-side copy](server-side-copy.en.md)) | Applications that need POSIX operations (rename, append, permission changes) | S14 |

## How to choose

| Condition | Path to consider first | What to confirm |
|---|---|---|
| The application accepts only file paths and mostly reads | a or c | For a, confirm on a real file system that Mountpoint accepts an FSx for ONTAP access point. For c, the design of client identities and ACLs |
| Bulk copy, scheduled sync, batch ingest | b | Whether the tool accepts the access point alias, and whether it issues operations that the compatibility list marks as not supported |
| An application that uses rename, append, or permission changes | c | How the same data will be used from the S3 API side |
| You want to narrow S3-side permissions with IAM and the access point | a or b | The permissions of the access point's file system user remain the real upper bound |
| Moving data to and from a bucket in another account | b | Same-Region copies only. [Server-side copy](server-side-copy.en.md) |

## Results of the 2026-11-24 run

Paths a and b were each checked once on a real file system on 2026-11-24 ([2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md)). Mountpoint for Amazon S3 mounted the FSx for ONTAP access point by both alias and ARN. New writes, reads, overwrite and delete (with the flags), rename and append gave the same results as a mount of an ordinary bucket in the same run. Path c (NFS) was not checked.
