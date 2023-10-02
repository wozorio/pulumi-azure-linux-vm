"""An Azure RM Python Pulumi program"""

import network
import nsg
import public_ip
import pulumi
import vm
from pulumi_azure_native import resources

config = pulumi.Config()

admin_username = config.get("adminUsername")
ssh_public_key = config.get("sshPublicKey")

# Create an Azure Resource Group
resource_group = resources.ResourceGroup('serverResourceGroup')

# Create an Azure Virtual Network
subnet = network.create_virtual_network(resource_group.name, resource_group.location)

# Create a Network Security Group and respective rules
network_security_group = nsg.create_network_security_group("resourceGroup")

nsg.create_nsg_rule(network_security_group.resource_group_name, network_security_group.name, "Rule1", priority=100, protocol="Tcp", destination_port_range="80", source_address_prefix="*")
nsg.create_nsg_rule(network_security_group.resource_group_name, network_security_group.name, "Rule2", priority=200, protocol="Tcp", destination_port_range="22", source_address_prefix="*")


# Create a public IP
public_ip_ = public_ip.create_public_ip(resource_group.name, resource_group.location)

# Create a virtual machine
server = vm.create_vm(resource_group.name, resource_group.location, admin_username, ssh_public_key, subnet.id)

# Export the public IP address of our VM
pulumi.export('publicIP', public_ip_.ip_address)
