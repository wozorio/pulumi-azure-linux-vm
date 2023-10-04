# Pulumi Azure

[![GitHub](https://img.shields.io/github/license/wozorio/pulumi-azure-linux-vm)](https://github.com/wozorio/pulumi-azure-linux-vm/blob/master/LICENSE)
[![CI](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/ci.yml/badge.svg)](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/ci.yml)
[![Deploy](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/deploy.yml/badge.svg)](https://github.com/wozorio/pulumi-azure-linux-vm/actions/workflows/deploy.yml)

Pulumi Python code for deploying a Linux VM with Ubuntu 22.04 LTS (Jammy Jellyfish) in Azure with GitHub Actions.

## Running it locally

### Prerequisites

1. Install Pulumi

   ```bash
   curl -fsSL https://get.pulumi.com | sh
   ```

1. Clone the repository and change to it

   ```bash
   git clone https://github.com/wozorio/pulumi-azure-linux-vm.git
   cd pulumi-azure-linux-vm
   ```

1. Install requirements

   ```bash
   pip install poetry
   poetry install --without dev
   ```

1. Login to Azure

   ```bash
   az login
   ```

1. Run Pulumi
   ```bash
   pulumi up
   ```
