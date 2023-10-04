"""Module to deploy a Linux virtual machine."""
from pulumi_azure_native import compute


def create_vm(name, resource_group_name, location, **kwargs) -> None:
    """Create a Linux VM."""
    ssh_public_key = read_file_content("id_rsa.pub")

    compute.VirtualMachine(
        name,
        resource_group_name=resource_group_name,
        location=location,
        os_profile=compute.OSProfileArgs(
            admin_username=kwargs.get("admin_username"),
            computer_name=name,
            linux_configuration=compute.LinuxConfigurationArgs(
                disable_password_authentication=True,
                ssh=compute.SshConfigurationArgs(
                    public_keys=[
                        compute.SshPublicKeyArgs(
                            path=(f"/home/{kwargs.get('admin_username')}/.ssh/authorized_keys"),
                            key_data=ssh_public_key,
                        )
                    ],
                ),
            ),
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(
                    id=kwargs.get("network_interface_id"),
                ),
            ],
        ),
        hardware_profile=compute.HardwareProfileArgs(
            vm_size=kwargs.get("vm_size", "Standard_B2s"),
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                publisher=kwargs.get("publisher", "canonical"),
                offer=kwargs.get("offer", "0001-com-ubuntu-server-jammy"),
                sku=kwargs.get("sku", "22_04-lts-gen2"),
                version=kwargs.get("version", "latest"),
            ),
        ),
        tags=kwargs.get("tags"),
    )


def read_file_content(file_path) -> str:
    """Helper function to read file content."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
