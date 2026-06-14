# ═════════════════════════════════════════════════════════════════════════
# Terraform - Oracle Cloud Infrastructure para BBVA Seguros
# ═════════════════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }

  # Descomenta para usar remote state
  # backend "s3" {
  #   bucket         = "bbva-terraform-state"
  #   key            = "prod/terraform.tfstate"
  #   region         = "us-ashburn-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "oci" {
  region       = var.oci_region
  auth         = "SecurityToken"
  config_file_directory = "~/.oci"
}

# ─────────────────────────────────────────────────────────────────────────
# VCN (Virtual Cloud Network)
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_vcn" "bbva_vcn" {
  compartment_id = var.oci_compartment_id
  display_name   = "bbva-seguros-vcn"
  cidr_blocks    = ["10.0.0.0/16"]
}

# ─────────────────────────────────────────────────────────────────────────
# Subnet pública
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_subnet" "bbva_public_subnet" {
  compartment_id      = var.oci_compartment_id
  vcn_id              = oci_core_vcn.bbva_vcn.id
  display_name        = "bbva-public-subnet"
  cidr_block          = "10.0.1.0/24"
  route_table_id      = oci_core_route_table.bbva_public_route_table.id
  security_list_ids   = [oci_core_security_list.bbva_public_security_list.id]
}

# ─────────────────────────────────────────────────────────────────────────
# Subnet privada para base de datos
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_subnet" "bbva_private_subnet" {
  compartment_id            = var.oci_compartment_id
  vcn_id                    = oci_core_vcn.bbva_vcn.id
  display_name              = "bbva-private-subnet"
  cidr_block                = "10.0.2.0/24"
  route_table_id            = oci_core_route_table.bbva_private_route_table.id
  security_list_ids         = [oci_core_security_list.bbva_private_security_list.id]
  prohibit_public_ip_on_vnic = true
}

# ─────────────────────────────────────────────────────────────────────────
# Internet Gateway
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_internet_gateway" "bbva_igw" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.bbva_vcn.id
  display_name   = "bbva-igw"
}

# ─────────────────────────────────────────────────────────────────────────
# Route Tables
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_route_table" "bbva_public_route_table" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.bbva_vcn.id
  display_name   = "bbva-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.bbva_igw.id
  }
}

resource "oci_core_route_table" "bbva_private_route_table" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.bbva_vcn.id
  display_name   = "bbva-private-rt"
}

# ─────────────────────────────────────────────────────────────────────────
# Security Lists
# ─────────────────────────────────────────────────────────────────────────

resource "oci_core_security_list" "bbva_public_security_list" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.bbva_vcn.id
  display_name   = "bbva-public-sl"

  # HTTP
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "0.0.0.0/0"
    destination_port_range {
      min = 80
      max = 80
    }
  }

  # HTTPS
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "0.0.0.0/0"
    destination_port_range {
      min = 443
      max = 443
    }
  }

  # Backend API
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "0.0.0.0/0"
    destination_port_range {
      min = 8000
      max = 8000
    }
  }

  # SSH (solo desde VCN)
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "10.0.0.0/16"
    destination_port_range {
      min = 22
      max = 22
    }
  }

  # Salida
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

resource "oci_core_security_list" "bbva_private_security_list" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.bbva_vcn.id
  display_name   = "bbva-private-sl"

  # PostgreSQL desde subnets públicas
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "10.0.1.0/24"
    destination_port_range {
      min = 5432
      max = 5432
    }
  }

  # Salida
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# ─────────────────────────────────────────────────────────────────────────
# Oracle Vault para secretos
# ─────────────────────────────────────────────────────────────────────────

resource "oci_kms_vault" "bbva_vault" {
  compartment_id = var.oci_compartment_id
  display_name   = "bbva-seguros-vault"
  vault_type     = "DEFAULT"
}

resource "oci_kms_key" "bbva_key" {
  compartment_id      = var.oci_compartment_id
  display_name        = "bbva-seguros-key"
  key_shape {
    algorithm = "AES"
    length    = 32
  }
  management_endpoint = oci_kms_vault.bbva_vault.management_endpoint
}

# ─────────────────────────────────────────────────────────────────────────
# Salidas
# ─────────────────────────────────────────────────────────────────────────

output "vcn_id" {
  value       = oci_core_vcn.bbva_vcn.id
  description = "VCN ID"
}

output "public_subnet_id" {
  value       = oci_core_subnet.bbva_public_subnet.id
  description = "Public Subnet ID para Container Instances"
}

output "private_subnet_id" {
  value       = oci_core_subnet.bbva_private_subnet.id
  description = "Private Subnet ID para Base de Datos"
}

output "vault_id" {
  value       = oci_kms_vault.bbva_vault.id
  description = "Vault ID para secretos"
}

output "key_id" {
  value       = oci_kms_key.bbva_key.id
  description = "Encryption Key ID"
}
