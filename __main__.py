"""An Azure RM Python Pulumi program"""

import pulumi
import vm
from pulumi_azure_native import network, resources

TAGS = {"created_by": "pulumi"}


def main() -> None:
    """The main function."""
    config = pulumi.Config()
    admin_username = config.get("admin_username")
    virtual_network_address_space = config.get("virtual_network_address_space")
    subnet_address_space = config.get("subnet_address_space")
    private_ip_address = config.get("private_ip_address")

    resource_group = resources.ResourceGroup("playground", tags=TAGS)

    virtual_network = create_virtual_network(
        "vnet",
        resource_group.name,
        resource_group.location,
        virtual_network_address_space=virtual_network_address_space,
        tags=TAGS,
    )

    subnet = create_subnet("snet", resource_group.name, virtual_network.name, subnet_address_space=subnet_address_space)

    public_ip = create_public_ip("pip-ubuntu", resource_group.name, resource_group.location, tags=TAGS)

    network_interface = create_network_interface(
        "nic_ubuntu",
        resource_group.name,
        subnet_id=subnet.id,
        private_ip_address=private_ip_address,
        public_ip_address_id=public_ip.id,
        tags=TAGS,
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

    vm.create_vm(
        "ubuntu",
        resource_group.name,
        resource_group.location,
        admin_username=admin_username,
        network_interface_id=network_interface.id,
        subnet_id=subnet.id,
        tags=TAGS,
    )

    pulumi.export("Ubuntu VM public IP", public_ip.ip_address)


def create_virtual_network(name: str, resource_group_name: str, location: str, **kwargs) -> network.VirtualNetwork:
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


def create_subnet(name: str, resource_group_name: str, virtual_network_name: str, **kwargs) -> network.Subnet:
    """Create a subnet."""
    subnet = network.Subnet(
        name,
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=kwargs.get("subnet_address_space"),
    )
    return subnet


def create_public_ip(name: str, resource_group_name: str, location: str, **kwargs) -> network.PublicIPAddress:
    """Create a public IP."""
    public_ip = network.PublicIPAddress(
        name,
        resource_group_name=resource_group_name,
        location=location,
        public_ip_allocation_method="Dynamic",
        sku=network.PublicIPAddressSkuArgs(name="Basic"),
        dns_settings=network.PublicIPAddressDnsSettingsArgs(domain_name_label="vm-ubuntu"),
        public_ip_address_version="IPv4",
        tags=kwargs.get("tags"),
    )
    return public_ip


def create_network_interface(name: str, resource_group_name: str, **kwargs) -> network.NetworkInterface:
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
                public_ip_address=network.PublicIPAddressArgs(
                    id=kwargs.get("public_ip_address_id"),
                ),
            )
        ],
        tags=kwargs.get("tags"),
    )
    return network_interface


def create_network_security_group(
    name: str, resource_group_name: str, location: str, **kwargs
) -> network.NetworkSecurityGroup:
    """Create a network security group."""
    nsg = network.NetworkSecurityGroup(
        name, resource_group_name=resource_group_name, location=location, tags=kwargs.get("tags")
    )
    return nsg


def create_nsg_rule(name: str, resource_group_name: str, network_security_group_name: str, **kwargs) -> None:
    """Create a NSG rule."""
    network.SecurityRule(
        name,
        resource_group_name=resource_group_name,
        network_security_group_name=network_security_group_name,
        priority=kwargs.get("priority"),
        direction=kwargs.get("direction", "Inbound"),
        access=kwargs.get("access", "Allow"),
        protocol=kwargs.get("protocol", "Tcp"),
        source_port_range=kwargs.get("source_port_range"),
        destination_port_range=kwargs.get("destination_port_range"),
        source_address_prefix=kwargs.get("source_address_prefix"),
        destination_address_prefix=kwargs.get("destination_address_prefix"),
    )


if __name__ == "__main__":
    main()
