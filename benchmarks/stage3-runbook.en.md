# Stage 3 runbook: checks on a real file system

🌐 **Language**: [日本語](stage3-runbook.md) | **English**

> **Conditions for running**: A real run costs money. Run it only inside the owner's approval and cost cap. The scripts are a dry run by default that creates nothing, and they create resources only with `--execute`. Real values of IDs, account IDs and aliases live in a configuration file outside the repository, and records redact them.

## Purpose and scope

On a real file system, check per case what AWS CLI, s5cmd, rclone and Mountpoint for Amazon S3 can do against S3 Access Points for FSx for ONTAP. Also check whether each tool issues a server-side copy (`CopyObject`, `UploadPartCopy`). AWS Transfer Family, File Mover Express and LucidLink are out of scope.

## Approval conditions and cap

- The cost cap is 20 USD. If the [cost estimate](#cost-estimate) exceeds the cap, nothing is created.
- The existing FSx for ONTAP is not changed. Only one dedicated test volume, one S3 Access Points, one S3 bucket, and one EC2 instance with its IAM role are created.
- Every resource gets the tags `Project=client-access-patterns` and `Run=<date and time>`. Settings that make a resource impossible to delete, such as deletion protection or retention periods, are not used.
- AWS authentication is SSO. On `Token has expired`, stop and ask the user to run `aws sso login`.

## Resources and naming

| Resource | Name | Create command | Delete command |
|---|---|---|---|
| S3 bucket (control and copy source) | `s3apbench-<datetime>-<random>` | `aws s3api create-bucket` | `aws s3 rm`, `aws s3api delete-bucket` |
| Dedicated test volume | `s3apbench_<datetime>` | `aws fsx create-volume` | `aws fsx delete-volume` |
| S3 Access Points | `s3apbench-<datetime>` | `aws fsx create-and-attach-s3-access-point` | `aws fsx detach-and-delete-s3-access-point` |
| IAM role and instance profile | `s3apbench-<datetime>-role`, `-profile` | `aws iam create-role` and others | `aws iam delete-role` and others |
| EC2 client (c6in.xlarge) | Tag `Name=s3apbench-<datetime>` | `aws ec2 run-instances` | `aws ec2 terminate-instances` |

The test volume is dedicated because a volume that had S3 Access Points attached cannot be deleted from ONTAP even after the access points are removed, and must be deleted through the FSx for ONTAP API ([Playbook constraints note](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md), Japanese). Nothing is attached to an existing volume, so existing configuration is unaffected.

## Procedure

1. Copy `benchmarks/stage3.env.example` to `~/.config/s3ap-client-patterns/stage3.env` and fill in real values. Confirm that the SVM has no ONTAP object store server.
2. Check every command that would be created with a dry run.
3. Create the resources with `--execute`. The created IDs are recorded in the state file.
4. Enter the client with Session Manager and wait for `/opt/stage3/.ready` (the mark that tool installation has finished).
5. Run the cases on the client. The tool versions are recorded in `versions.txt` at run time.
6. Move the evidence from the client to the bucket, and from the bucket to `benchmarks/records/<datetime>/raw/` on the operator machine.
7. Write the record (template: [benchmark-record.en.md](../docs/templates/benchmark-record.en.md)). Redact real values.
8. Run the cleanup script and add the read-back and zero-remaining checks to the record.

```bash
benchmarks/scripts/stage3-setup.sh --dry-run
benchmarks/scripts/stage3-setup.sh --execute
aws ssm start-session --region ap-northeast-1 --target <instance id>
/opt/stage3/stage3-measure.sh --execute --case all
benchmarks/scripts/stage3-export-evidence.sh --execute
benchmarks/scripts/stage3-teardown.sh --execute
```

## What each case checks

| Case | Control (an operation that should succeed) | What is checked | Evidence |
|---|---|---|---|
| control | List, write and read on an ordinary S3 bucket | Whether list, write, read and `HeadObject` work with the alias and the ARN, and whether the hash of the retrieved content matches | `control-*.json`, `hashes.tsv` |
| aws-cli | `cp`, `sync` and `rm` on an ordinary bucket | With both alias and ARN: `cp` of 1 MiB and 64 MiB (multipart), `sync`, `--no-overwrite`, `rm`. The API names shown by `--debug` | `awscli-*.log`, `probes.tsv` |
| s5cmd | `ls`, `cp` and `rm` on an ordinary bucket | Whether it accepts the alias, whether it works without `--endpoint-url`, and the error when it fails | `probe-s5cmd-*.log` |
| rclone | `lsf`, `copyto` and `check` on an ordinary bucket | Whether it reaches the alias with `force_path_style = false`, the result of `check`, and the headers in `--dump headers` | `probe-rclone-*.log` |
| mountpoint | The same operations on a mount of an ordinary bucket | Whether it mounts with the alias and the ARN, the results of a new write, overwrite, rename, append, `mkdir` and delete, and the difference with `--allow-overwrite` and `--allow-delete`. The difference from the NFS path (optional) | `probe-mp-*.log`, `mp-*-logs/` |
| server-side-copy | A direct `aws s3api copy-object` | Each tool's sent and received bytes, the API names in `--debug` and `--dump headers`, and the hash after the copy. The difference from a download-and-upload reference | `nic.tsv`, `probe-ssc-*.log`, `hashes.tsv` |

## Cleanup script and evidence export

Things that disappear at teardown (bucket contents, files on the throwaway volume, logs on the client) are moved out before teardown.

1. On the client, run `stage3-measure.sh --execute --case export` to put the results under `evidence/` in the bucket (it is part of `--case all`).
2. On the operator machine, run `stage3-export-evidence.sh --execute` to copy them to `benchmarks/records/<datetime>/raw/`. The describe output of the resources goes there too.
3. While `raw/` is empty, `stage3-teardown.sh` stops without deleting anything.
4. Run `stage3-teardown.sh --execute`. The deletion order is S3 Access Points, volume, EC2, role, bucket. The IDs come from the state file, and the volume is deleted only when its `Run` tag equals this run's value.
5. About every 15 seconds each resource is described to read back that it is gone. The result stays in `raw/teardown-readback.tsv`.
6. Search by the `Run` tag and confirm in `raw/teardown-tag-search.json` that nothing remains.

If deleting a created resource fails, do not rerun. Report the remaining resource IDs and the cost that is still accruing.

## IAM permissions per actor

| Actor | Actions | When used |
|---|---|---|
| Operator (SSO administrator role) | `fsx:CreateVolume`, `fsx:CreateAndAttachS3AccessPoint`, `s3:CreateAccessPoint`, `s3:GetAccessPoint`, `fsx:DescribeVolumes`, `fsx:DescribeS3AccessPointAttachments`, `fsx:TagResource` | Creating and checking the volume and the access point |
| Operator | `fsx:DetachAndDeleteS3AccessPoint`, `fsx:DeleteVolume`, `s3:DeleteAccessPoint` (whether it is needed is unconfirmed) | Cleanup |
| Operator | `ec2:RunInstances`, `ec2:TerminateInstances`, `ec2:DescribeInstances`, `iam:CreateRole`, `iam:PutRolePolicy`, `iam:PassRole` and others | Creating and deleting the client and the role |
| Operator | `s3:CreateBucket`, `s3:PutBucketTagging`, `s3:DeleteBucket`, `tag:GetResources` | Creating and deleting the bucket, and the tag search |
| EC2 instance role | `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:GetObjectTagging`, `s3:PutObjectTagging`, `s3:AbortMultipartUpload`, `s3:ListMultipartUploadParts` (on both the access point and the bucket) | Reads, writes and copies by each tool |
| EC2 instance role | `s3:ListBucket`, `s3:GetBucketLocation`, `s3:ListBucketMultipartUploads` (on both the access point and the bucket) | Listing and the Mountpoint mount |
| EC2 instance role | `AmazonSSMManagedInstanceCore` | Connecting with Session Manager |

The instance role policy is [stage3-instance-policy.json](stage3-instance-policy.json). Access points are limited to `s3apbench-*`, and the bucket (`example-bucket` in the file) is replaced with this run's name at run time.

## Cost estimate

The estimate uses the ap-northeast-1 unit prices read on 2026-11-24 from the Pricing API (and the FSx for ONTAP and S3 pricing pages). The prices are effective from 2026-11-01 (IPv4 from 2026-11-17). The run takes at most 4 hours, and the request counts are assumed upper bounds.

| Item | Assumption | Unit price | Estimate (USD) |
|---|---|---|---|
| EC2 c6in.xlarge | Linux, on-demand, 4 hours | 0.2856 USD/hour | 1.14 |
| EBS gp3 | 8 GiB, 4 hours | 0.096 USD/GB-month | 0.00 |
| S3 PUT, COPY, POST, LIST | 10,000 requests (assumed upper bound) | 0.0047 USD/1,000 requests | 0.05 |
| S3 GET and other | 50,000 requests (assumed upper bound) | 0.0037 USD/10,000 requests | 0.02 |
| S3 storage | 2 GiB, 4 hours | 0.025 USD/GB-month | 0.00 |
| Public IPv4 | 1 address, 4 hours (if attached) | 0.005 USD/hour | 0.02 |
| FSx for ONTAP | A dedicated volume in existing free capacity. No added charge (inside the provisioned capacity) | - | 0.00 |
| Total |  |  | about 1.2 |

> **Assumptions and exclusions**: Same-Region data transfer with S3 is what the S3 pricing page lists as not charged. The existing FSx for ONTAP (1,024 GiB SSD, 128 MBps, single AZ) costs 0.15 USD/GB-month and 0.906 USD/MBps-month (about 0.37 USD/hour) and is already running, so it is not an increment. The FSx for ONTAP pricing page lists only S3 requests and data transfer for S3 Access Points. Even if the time doubles (8 hours) the total is about 2.4 USD, far from the 20 USD cap.

## What is not confirmed

- Whether `s3:DeleteAccessPoint` is needed to delete the access point. If it is, a permission error shows it at run time and the operator role is extended.
- Whether the Session Manager plugin is installed on the operator machine.
- Whether the Mountpoint version installed by `dnf` is the latest (1.25.0). It is recorded in `versions.txt` at run time.
- That the test SVM has no ONTAP object store server. If it has one, creating the access point fails (Playbook).
- A CloudTrail data-event check of `CopyObject`. The scripts do not include it; add it by hand after approval if needed.
