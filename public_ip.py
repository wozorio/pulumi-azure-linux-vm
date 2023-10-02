from pulumi_azure_native import network


def create_public_ip(resource_group_name, location):
    # Create public IP
    public_ip = network.PublicIPAddress("serverPublicIp",
        resource_group_name=resource_group_name,
        location=location,
        public_ip_allocation_method='Static'
    )
    return public_ip
