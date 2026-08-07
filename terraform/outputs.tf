output "resource_group_name" {
  description = "Azure resource group"
  value       = azurerm_resource_group.ai.name
}

output "vm_public_ip" {
  description = "Public IP address of the AI DevOps VM"
  value       = azurerm_public_ip.ai.ip_address
}

output "vm_name" {
  description = "Azure VM name"
  value       = azurerm_linux_virtual_machine.ai.name
}

output "ssh_command" {
  description = "SSH command for connecting to the VM"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.ai.ip_address}"
}