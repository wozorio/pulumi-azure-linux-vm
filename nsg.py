from pulumi_azure_native import resources, network

def create_network_security_group(resource_group_name):
    resource_group = resources.ResourceGroup(resource_group_name)

    nsg = network.NetworkSecurityGroup(
        resource_group_name + "NSG",
        resource_group_name=resource_group_name,
        location=resource_group.location
    )
    
    return nsg

def create_nsg_rule(resource_group_name, nsg_name, rule_name, **kwargs) -> network.SecurityRule:
    # Use `get` method to provide a default value if a key doesn't exist.
    protocol = kwargs.get("protocol", "Tcp")
    destination_port_range = kwargs.get("destination_port_range", "22-80")
    source_address_prefix = kwargs.get("source_address_prefix", "*")

    nsg_rule = network.SecurityRule(
        rule_name,
        resource_group_name=resource_group_name,
        network_security_group_name=nsg_name,
        protocol=protocol,
        destination_port_range=destination_port_range,
        source_address_prefix=source_address_prefix,
        access=kwargs.get("access", "Allow"),
        direction=kwargs.get("direction", "Inbound"),
        priority=kwargs.get("priority"),
    )

    return nsg_rule
