#!/usr/bin/env bash
# EC2 user data for the stage 3 client (Amazon Linux 2023, x86_64). Runs once as root at first boot.
# Installs pinned tool versions and fetches the run values and scripts from the comparison bucket.
set -eu
S5CMD_VERSION=2.3.0
RCLONE_VERSION=v1.76.0
TOKEN="$(curl -sS -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 300')" # allow:safety (the instance metadata address)
BUCKET="$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/tags/instance/stage3-bucket)" # allow:safety (the instance metadata address)
dnf install -y mount-s3 unzip nfs-utils
cd /tmp
curl -sSLO "https://github.com/peak/s5cmd/releases/download/v${S5CMD_VERSION}/s5cmd_${S5CMD_VERSION}_Linux-64bit.tar.gz"
tar -xzf "s5cmd_${S5CMD_VERSION}_Linux-64bit.tar.gz" s5cmd
install -m 0755 s5cmd /usr/local/bin/s5cmd
curl -sSLO "https://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip"
unzip -q -o "rclone-${RCLONE_VERSION}-linux-amd64.zip"
install -m 0755 "rclone-${RCLONE_VERSION}-linux-amd64/rclone" /usr/local/bin/rclone
mkdir -p /opt/stage3
aws s3 cp "s3://${BUCKET}/config/stage3-client.env" /etc/stage3.env
aws s3 cp "s3://${BUCKET}/scripts/" /opt/stage3/ --recursive
chmod +x /opt/stage3/*.sh
touch /opt/stage3/.ready
