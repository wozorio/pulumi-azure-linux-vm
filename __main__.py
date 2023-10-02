"""An Azure RM Python Pulumi program"""

import nsg
import pulumi
import vm
from pulumi_azure_native import network, resources


def main():
    """The main function."""
    config = pulumi.Config()

    admin_username = config.get("adminUsername")
    ssh_public_key = config.get("sshPublicKey")

    resource_group = resources.ResourceGroup("playground")

    virtual_network = create_virtual_network(resource_group.name, resource_group.location)
    subnet = create_subnet(resource_group.name, virtual_network.name)

    network_security_group = nsg.create_network_security_group("resourceGroup")
    nsg.create_nsg_rule(
        network_security_group.resource_group_name,
        network_security_group.name,
        "Rule1",
        priority=100,
        protocol="Tcp",
        destination_port_range="80",
        source_address_prefix="*",
    )
    nsg.create_nsg_rule(
        network_security_group.resource_group_name,
        network_security_group.name,
        "Rule2",
        priority=200,
        protocol="Tcp",
        destination_port_range="22",
        source_address_prefix="*",
    )

    public_ip = create_public_ip(resource_group.name, resource_group.location)

    vm.create_vm(resource_group.name, resource_group.location, admin_username, ssh_public_key, subnet.id)

    # Export the public IP address of the VM
    pulumi.export("publicIP", public_ip.ip_address)


def create_virtual_network(resource_group_name, location):
    """Create a virtual network."""
    virtual_network = network.VirtualNetwork(
        "serverNetwork",
        resource_group_name=resource_group_name,
        location=location,
        address_space=network.AddressSpaceArgs(
            address_prefixes=["10.0.0.0/16"],
        ),
    )
    return virtual_network


def create_subnet(resource_group_name, virtual_network_name):
    """Create a subnet."""
    subnet = network.Subnet(
        "serverSubnet",
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix="10.0.1.0/24",
    )
    return subnet


def create_public_ip(resource_group_name, location):
    """Create a public IP."""
    public_ip = network.PublicIPAddress(
        "serverPublicIp", resource_group_name=resource_group_name, location=location, public_ip_allocation_method="Static"
    )
    return public_ip


if __name__ == "__main__":
    main()
