from pulumi_azure_native import compute


def create_vm(resource_group_name, location, admin_username, ssh_public_key, network_interface_id):
    # Create Linux VM
    vm = compute.VirtualMachine("serverVM",
        resource_group_name=resource_group_name,
        location=location,
        os_profile=compute.OSProfileArgs(
            admin_username=admin_username,
            computer_name="hostname",
            linux_configuration=compute.LinuxConfigurationArgs(
                disable_password_authentication=True,
                ssh=compute.SshConfigurationArgs(
                    public_keys=[
                        compute.SshPublicKeyArgs(
                            path="/home/username/.ssh/authorized_keys",
                            key_data=ssh_public_key,
                        )
                    ],
                ),
            ),
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(
                    id=network_interface_id,
                ),
            ],
        ),
        hardware_profile=compute.HardwareProfileArgs(
            vm_size="Standard_A0",
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                publisher="canonical",
                offer="UbuntuServer",
                sku="22_04-lts",
                version="latest",
            ),
        ),
    )

    return vm
