# Pulumi Azure

[![GitHub](https://img.shields.io/github/license/wozorio/pulumi-azure-linux-vm)](https://github.com/wozorio/pulumi-azure-linux-vm/blob/master/LICENSE)
[![CI](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/ci.yml/badge.svg)](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/ci.yml)
[![Deploy](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/deploy.yml/badge.svg)](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/deploy.yml)

Pulumi Python code for deploying a Linux VM with Ubuntu 24.04 LTS in Azure.

## Running it locally

1. Clone the repository and change directory

   ```bash
   git clone https://github.com/wozorio/pulumi-azure-linux-vm.git
   cd pulumi-azure-linux-vm
   ```

1. Install requirements

   ```bash
   uv sync
   ```

1. Login to Azure

   ```bash
   az login
   ```

1. Run Pulumi
   ```bash
   pulumi up
   ```
