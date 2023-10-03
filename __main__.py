"""An Azure RM Python Pulumi program"""

import pulumi
import vm
from pulumi_azure_native import network, resources

TAGS = {"created_by": "pulumi"}


def main():
    """The main function."""
    config = pulumi.Config()
    admin_username = config.get("admin_username")
    private_ip_address = config.get("private_ip_address")
    virtual_network_address_space = config.get("virtual_network_address_space")
    subnet_address_space = config.get("subnet_address_space")

    resource_group = resources.ResourceGroup("playground-wozorio", tags=TAGS)

    virtual_network = create_virtual_network(
        "vnet",
        resource_group.name,
        resource_group.location,
        virtual_network_address_space=virtual_network_address_space,
        tags=TAGS,
    )

    subnet = create_subnet("snet", resource_group.name, virtual_network.name, subnet_address_space=subnet_address_space)

    network_interface = create_network_interface(
        "nic_ubuntu", resource_group.name, subnet_id=subnet.id, private_ip_address=private_ip_address, tags=TAGS
    )

    network_security_group = create_network_security_group("nsg", resource_group.name, resource_group.location, tags=TAGS)
    pulumi.Output.all(resource_group.name, network_security_group.name).apply(
        lambda args: create_nsg_rule(
            "Allow-HTTP-From-Internet-To-VM",
            args[0],
            args[1],
            priority=100,
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="80",
            source_address_prefix="Internet",
            destination_address_prefix=f"{private_ip_address}/32",
        )
    )
    pulumi.Output.all(resource_group.name, network_security_group.name).apply(
        lambda args: create_nsg_rule(
            "Allow-SSH-From-Internet-To-VM",
            args[0],
            args[1],
            priority=200,
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="Internet",
            destination_address_prefix=f"{private_ip_address}/32",
        )
    )

    public_ip = create_public_ip("pip-ubuntu", resource_group.name, resource_group.location, tags=TAGS)

    vm.create_vm(
        "ubuntu",
        resource_group.name,
        resource_group.location,
        admin_username=admin_username,
        network_interface_id=network_interface.id,
        public_ip_address=public_ip.id,
        subnet_id=subnet.id,
        tags=TAGS,
    )

    pulumi.export("Ubuntu VM public IP", public_ip.ip_address)


def create_virtual_network(name, resource_group_name, location, **kwargs):
    """Create a virtual network."""
    virtual_network = network.VirtualNetwork(
        name,
        resource_group_name=resource_group_name,
        location=location,
        address_space=network.AddressSpaceArgs(
            address_prefixes=[kwargs.get("virtual_network_address_space")],
        ),
        tags=kwargs.get("tags"),
    )
    return virtual_network


def create_subnet(name, resource_group_name, virtual_network_name, **kwargs):
    """Create a subnet."""
    subnet = network.Subnet(
        name,
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=kwargs.get("subnet_address_space"),
    )
    return subnet


def create_network_interface(name, resource_group_name, **kwargs):
    """Create a network interface."""
    network_interface = network.NetworkInterface(
        name,
        resource_group_name=resource_group_name,
        ip_configurations=[
            network.NetworkInterfaceIPConfigurationArgs(
                name="ipconfig",
                subnet=network.SubnetArgs(id=kwargs.get("subnet_id")),
                private_ip_allocation_method=kwargs.get("private_ip_allocation_method", "Static"),
                private_ip_address=kwargs.get("private_ip_address"),
                public_ip_address=kwargs.get("public_ip_address"),
            )
        ],
        tags=kwargs.get("tags"),
    )
    return network_interface


def create_network_security_group(name, resource_group_name, location, **kwargs):
    """Create a network security group."""
    nsg = network.NetworkSecurityGroup(
        name, resource_group_name=resource_group_name, location=location, tags=kwargs.get("tags")
    )
    return nsg


def create_nsg_rule(name, resource_group_name, network_security_group_name, **kwargs) -> network.SecurityRule:
    """Create a NSG rule."""
    nsg_rule = network.SecurityRule(
        name,
        resource_group_name=resource_group_name,
        network_security_group_name=network_security_group_name,
        protocol=kwargs.get("protocol", "Tcp"),
        source_port_range=kwargs.get("source_port_range"),
        destination_port_range=kwargs.get("destination_port_range"),
        source_address_prefix=kwargs.get("source_address_prefix"),
        destination_address_prefix=kwargs.get("destination_address_prefix"),
        access=kwargs.get("access", "Allow"),
        direction=kwargs.get("direction", "Inbound"),
        priority=kwargs.get("priority"),
    )
    return nsg_rule


def create_public_ip(name, resource_group_name, location, **kwargs):
    """Create a public IP."""
    public_ip = network.PublicIPAddress(
        name,
        resource_group_name=resource_group_name,
        location=location,
        public_ip_allocation_method="Dynamic",
        sku=network.PublicIPAddressSkuArgs(name="Basic"),
        dns_settings=network.PublicIPAddressDnsSettingsArgs(domain_name_label="vm-ubuntu9"),
        public_ip_address_version="IPv4",
        tags=kwargs.get("tags"),
    )
    return public_ip


if __name__ == "__main__":
    main()
