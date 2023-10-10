"""An Azure RM Python Pulumi program"""

import dataclasses

import pulumi
import vm
from pulumi_azure_native import network, resources

TAGS = {"created_by": "pulumi"}


@dataclasses.dataclass
class NSGRule:
    """Represent the properties of a NSG rule."""

    priority: int
    direction: str
    access: str
    protocol: str
    source_port_range: str
    destination_port_range: int
    source_address_prefix: str
    destination_address_prefix: str


def main() -> None:
    """The main function."""
    config = pulumi.Config()
    admin_username = config.get("admin_username")
    virtual_network_address_space = config.get("virtual_network_address_space")
    subnet_address_space = config.get("subnet_address_space")
    private_ip_address = config.get("private_ip_address")

    resource_group = resources.ResourceGroup("playground", tags=TAGS)

    network_security_group = create_network_security_group("nsg", resource_group.name, resource_group.location, tags=TAGS)
    create_nsg_rule(
        "Allow-HTTP-From-Internet-To-VM",
        resource_group.name,
        network_security_group.name.apply(lambda network_security_group_name: network_security_group_name),
        NSGRule(
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="80",
            source_address_prefix="Internet",
            destination_address_prefix=f"{private_ip_address}/32",
        ),
    )

    create_nsg_rule(
        "Allow-SSH-From-Internet-To-VM",
        resource_group.name,
        network_security_group.name.apply(lambda network_security_group_name: network_security_group_name),
        NSGRule(
            priority=200,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="Internet",
            destination_address_prefix=f"{private_ip_address}/32",
        ),
    )

    virtual_network = create_virtual_network(
        "vnet",
        resource_group.name,
        resource_group.location,
        virtual_network_address_space=virtual_network_address_space,
        tags=TAGS,
    )

    subnet = create_subnet(
        "snet",
        resource_group.name,
        virtual_network.name,
        subnet_address_space=subnet_address_space,
        network_security_group_id=network_security_group.id,
    )

    public_ip = create_public_ip(
        "pip-ubuntu", resource_group.name, resource_group.location, domain_name_label="vm-ubuntu", tags=TAGS
    )

    network_interface = create_network_interface(
        "nic_ubuntu",
        resource_group.name,
        subnet_id=subnet.id,
        private_ip_address=private_ip_address,
        public_ip_address_id=public_ip.id,
        tags=TAGS,
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

    pulumi.export("Virtual machine FQDN", public_ip.dns_settings.apply(lambda dns: dns.fqdn))


def create_network_security_group(
    name: str, resource_group_name: str, location: str, **kwargs
) -> network.NetworkSecurityGroup:
    """Create a network security group."""
    nsg = network.NetworkSecurityGroup(name, resource_group_name=resource_group_name, location=location, tags=kwargs["tags"])
    return nsg


def create_nsg_rule(name: str, resource_group_name: str, network_security_group_name: str, rule: NSGRule) -> None:
    """Create a NSG rule."""
    network.SecurityRule(
        name,
        resource_group_name=resource_group_name,
        network_security_group_name=network_security_group_name,
        priority=rule.priority,
        direction=rule.direction,
        access=rule.access,
        protocol=rule.protocol,
        source_port_range=rule.source_port_range,
        destination_port_range=rule.destination_port_range,
        source_address_prefix=rule.source_address_prefix,
        destination_address_prefix=rule.destination_address_prefix,
    )


def create_virtual_network(name: str, resource_group_name: str, location: str, **kwargs) -> network.VirtualNetwork:
    """Create a virtual network."""
    virtual_network = network.VirtualNetwork(
        name,
        resource_group_name=resource_group_name,
        location=location,
        address_space=network.AddressSpaceArgs(
            address_prefixes=[kwargs["virtual_network_address_space"]],
        ),
        tags=kwargs["tags"],
    )
    return virtual_network


def create_subnet(name: str, resource_group_name: str, virtual_network_name: str, **kwargs) -> network.Subnet:
    """Create a subnet."""
    subnet = network.Subnet(
        name,
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=kwargs["subnet_address_space"],
        network_security_group=network.NetworkSecurityGroupArgs(id=kwargs["network_security_group_id"]),
    )
    return subnet


def create_public_ip(name: str, resource_group_name: str, location: str, **kwargs) -> network.PublicIPAddress:
    """Create a public IP."""
    public_ip = network.PublicIPAddress(
        name,
        resource_group_name=resource_group_name,
        location=location,
        public_ip_allocation_method=kwargs.get("public_ip_allocation_method", "Dynamic"),
        sku=network.PublicIPAddressSkuArgs(name=kwargs.get("sku_name", "Basic")),
        dns_settings=network.PublicIPAddressDnsSettingsArgs(domain_name_label=kwargs["domain_name_label"]),
        public_ip_address_version=kwargs.get("public_ip_address_version", "IPv4"),
        tags=kwargs["tags"],
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
                subnet=network.SubnetArgs(id=kwargs["subnet_id"]),
                private_ip_allocation_method=kwargs.get("private_ip_allocation_method", "Static"),
                private_ip_address=kwargs["private_ip_address"],
                public_ip_address=network.PublicIPAddressArgs(
                    id=kwargs["public_ip_address_id"],
                ),
            )
        ],
        tags=kwargs["tags"],
    )
    return network_interface


if __name__ == "__main__":
    main()
