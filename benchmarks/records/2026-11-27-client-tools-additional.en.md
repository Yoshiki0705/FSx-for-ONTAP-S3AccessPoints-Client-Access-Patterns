# 2026-11-27 additional client tool checks
🌐 **Language**: [日本語](2026-11-27-client-tools-additional.md) | **English**
> **Class**: A sample run. On the same environment as the 2026-11-24 record ([stage 3](2026-11-24-client-tools-stage3.en.md)), I checked the reverse direction of server-side copy, large objects, use alongside NFS, and splitting access points, once each. No performance numbers were recorded. IDs, the account ID, and access point aliases are redacted.
## Environment
| Item | Entry |
|---|---|
| Date | 2026-11-27 01:33 to 02:17 (Japan time) |
| Region | ap-northeast-1 |
| FSx for ONTAP configuration | The same existing verification file system as stage 3 (first generation `SINGLE_AZ_1`, throughput capacity 128 MBps, SSD 1,024 GiB). A dedicated 20 GiB volume with the UNIX security style was created and deleted at teardown |
| ONTAP version | 9.19.1P4 (ONTAP REST `GET /api/cluster?fields=version`) |
| Client | EC2 c6in.xlarge, Amazon Linux 2023 (kernel 6.18), same subnet as the file system |
| Tools and versions | AWS CLI 2.38.0, s5cmd 2.3.0, rclone 1.76.0, Mountpoint for Amazon S3 1.24.0 |
| Object sizes | 256 MiB, 6 GiB (random content) |
| Repetitions and aggregation | One per operation. No aggregation |
| Measurement class | Sample run |
| Cleanup | The two extra access points were deleted, and the stage 3 script removed the rest. The S3 bucket, volume, access point, IAM role, and EC2 instance were read back with describe and were gone (the EC2 instance was `terminated`) |
## Server-side copy (volume to bucket, 256 MiB)
Sent plus received bytes are the difference of the transmitted and received bytes on the client's default-route network interface, read before and after the copy.
| Copy method | Result | Sent plus received (bytes) | Hash |
|---|---|---|---|
| `aws s3api copy-object` | Succeeded | 16,372 | Matched |
| `aws s3 cp` | Succeeded | 227,211 | Matched |
| `s5cmd cp` | Succeeded | 19,265 | Matched |
| `rclone copyto` (default) | Failed with `InvalidArgument: FSX_ONTAP is not allowed` | 82,449 | No destination |
| `rclone copyto --s3-storage-class STANDARD` | Succeeded | 49,100 | Matched |
## Server-side copy (6 GiB = 6,442,450,944 bytes)
| Direction | Copy method | Result | Sent plus received (bytes) | Hash |
|---|---|---|---|---|
| Bucket to volume | `aws s3api copy-object` | `InvalidRequest` (the source is larger than 5,368,709,120 bytes) | 16,423 | - |
| Bucket to volume | `aws s3 cp` | Succeeded (`UploadPartCopy`) | 3,358,458 | Matched |
| Bucket to volume | `s5cmd cp` | Failed with the same `InvalidRequest` | 16,313 | - |
| Bucket to volume | `rclone copyto --s3-storage-class FSX_ONTAP` | Succeeded | 969,668 | Matched |
| Volume to bucket | `aws s3 cp` | Succeeded | 3,026,741 | Matched |
## Use alongside NFS (version 4.1)
| Operation | Result |
|---|---|
| Read over NFS a file written over the S3 API (256 MiB) | Hash matched. Owner 0:2 (root:daemon), mode 644 |
| Read over the S3 API a file written over NFS (1 MiB) | Listed, hash matched |
| Rename and append over NFS, then read over the S3 API | Listed under the new name; content and size (1,048,585 bytes) matched the appended file |
| Delete over the S3 API, then look over NFS | The file was gone |
| Directories created over the S3 API | Both were `drwxrwxrwx` (777) |
## Splitting access points
Three access points were attached to one volume (VPC origin with `root`, VPC origin with `pcuser` (UID 65534), and internet origin with `root`).
| Operation | Result |
|---|---|
| `pcuser`: read the first 100 bytes of a file created by `root` | Succeeded |
| `pcuser`: write to a volume whose root is owned by `root` (mode 755) | `AccessDenied` |
| `pcuser`: write after changing the owner of the volume root to UID 65534 | Succeeded. The new file was owned by 65534:65534, mode 644 |
| `pcuser`: overwrite a `root`-owned file (mode 644) in a 777 directory | Succeeded |
| List a VPC-origin access point from outside the VPC (a laptop) | `AccessDenied` (explicit deny in a resource-based policy) |
| List, write, and `head-object` an internet-origin access point from the same laptop | Succeeded |
| One 100 MiB part of an incomplete multipart upload (volume used space read through ONTAP REST) | 274,239,488 bytes before, with the part in place, and after the abort. Not visible over NFS |
## Commands used
```sh
mount -t nfs -o vers=4.1 <NFS endpoint>:/<junction path> /mnt/nfs
rclone copyto "ap:<alias>/<key>" "ap:<bucket>/<key>" --s3-storage-class STANDARD
aws fsx create-and-attach-s3-access-point --name <name> --type ONTAP \
  --ontap-configuration "VolumeId=<volume ID>,FileSystemIdentity={Type=UNIX,UnixUser={Name=<UNIX user name>}}" \
  --s3-access-point "VpcConfiguration={VpcId=<VPC ID>}"
```
