from pulumi_azure_native import network


def create_virtual_network(resource_group_name, location):
    # Create virtual network
    virtual_network = network.VirtualNetwork("serverNetwork",
        resource_group_name=resource_group_name,
        location=location,
        address_space=network.AddressSpaceArgs(
            address_prefixes=["10.0.0.0/16"],
        )
    )

    # Create subnet
    subnet = network.Subnet("serverSubnet",
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network.name,
        address_prefix="10.0.1.0/24"
    )

    return subnet
