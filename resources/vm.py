"""Module to deploy a Linux virtual machine."""

from pulumi_azure_native import compute


def create_vm(name: str, resource_group_name: str, location: str, **kwargs) -> None:
    """Create a Linux VM."""
    ssh_public_key = read_file_content("id_rsa.pub").replace("\n", "")

    compute.VirtualMachine(
        name,
        resource_group_name=resource_group_name,
        location=location,
        os_profile=compute.OSProfileArgs(
            admin_username=kwargs["admin_username"],
            computer_name=name,
            linux_configuration=compute.LinuxConfigurationArgs(
                disable_password_authentication=True,
                ssh=compute.SshConfigurationArgs(
                    public_keys=[
                        compute.SshPublicKeyArgs(
                            path=(f"/home/{kwargs['admin_username']}/.ssh/authorized_keys"),
                            key_data=ssh_public_key,
                        )
                    ],
                ),
            ),
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(
                    id=kwargs["network_interface_id"],
                ),
            ],
        ),
        hardware_profile=compute.HardwareProfileArgs(
            vm_size=kwargs.get("vm_size", "Standard_B2s"),
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                publisher=kwargs.get("publisher", "canonical"),
                offer=kwargs.get("offer", "ubuntu-24_04-lts"),
                sku=kwargs.get("sku", "server"),
                version=kwargs.get("version", "latest"),
            ),
        ),
        tags=kwargs["tags"],
    )


def read_file_content(file_path: str) -> str:
    """Helper function to read file content."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
