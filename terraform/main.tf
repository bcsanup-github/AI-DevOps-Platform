terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# ---------------------------------------------------------
# Resource Group
# ---------------------------------------------------------
resource "azurerm_resource_group" "ai" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project     = "AI-DevOps-Platform"
    environment = "production"
    managed_by  = "terraform"
  }
}

# ---------------------------------------------------------
# Virtual Network
# ---------------------------------------------------------
resource "azurerm_virtual_network" "ai" {
  name                = "ai-devops-vnet"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name
  address_space       = ["10.0.0.0/16"]

  tags = {
    project = "AI-DevOps-Platform"
  }
}

# ---------------------------------------------------------
# Subnet
# ---------------------------------------------------------
resource "azurerm_subnet" "ai" {
  name                 = "ai-devops-subnet"
  resource_group_name  = azurerm_resource_group.ai.name
  virtual_network_name = azurerm_virtual_network.ai.name
  address_prefixes     = ["10.0.1.0/24"]
}

# ---------------------------------------------------------
# Network Security Group
# ---------------------------------------------------------
resource "azurerm_network_security_group" "ai" {
  name                = "ai-devops-nsg"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name

  # SSH
  security_rule {
    name                       = "Allow-SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # HTTP
  security_rule {
    name                       = "Allow-HTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # HTTPS
  security_rule {
    name                       = "Allow-HTTPS"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    project = "AI-DevOps-Platform"
  }
}

# ---------------------------------------------------------
# Public IP
# ---------------------------------------------------------
resource "azurerm_public_ip" "ai" {
  name                = "ai-devops-public-ip"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    project = "AI-DevOps-Platform"
  }
}

# ---------------------------------------------------------
# Network Interface
# ---------------------------------------------------------
resource "azurerm_network_interface" "ai" {
  name                = "ai-devops-nic"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ai.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ai.id
  }

  tags = {
    project = "AI-DevOps-Platform"
  }
}

# ---------------------------------------------------------
# Associate NSG with NIC
# ---------------------------------------------------------
resource "azurerm_network_interface_security_group_association" "ai" {
  network_interface_id      = azurerm_network_interface.ai.id
  network_security_group_id = azurerm_network_security_group.ai.id
}

# ---------------------------------------------------------
# Linux Virtual Machine
# ---------------------------------------------------------
resource "azurerm_linux_virtual_machine" "ai" {
  name                = "ai-devops-vm"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name
  size                = var.vm_size

  admin_username = var.admin_username

  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.ai.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  os_disk {
    name                 = "ai-devops-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  tags = {
    project     = "AI-DevOps-Platform"
    environment = "production"
    managed_by  = "terraform"
  }
}