# ═════════════════════════════════════════════════════════════════════════
# Variables de Terraform
# ═════════════════════════════════════════════════════════════════════════

variable "oci_region" {
  type        = string
  description = "Región de Oracle Cloud (e.g., us-ashburn-1, us-phoenix-1)"
  default     = "us-ashburn-1"
}

variable "oci_compartment_id" {
  type        = string
  description = "Compartment ID en Oracle Cloud"
  sensitive   = true
}

variable "app_name" {
  type        = string
  description = "Nombre de la aplicación"
  default     = "bbva-seguros"
}

variable "environment" {
  type        = string
  description = "Ambiente (development, staging, production)"
  default     = "production"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "El environment debe ser development, staging o production."
  }
}

variable "container_image" {
  type        = string
  description = "URL de la imagen Docker en OCIR"
  example     = "iad.ocir.io/namespace/bbva-seguros:latest"
}

variable "container_port" {
  type        = number
  description = "Puerto del contenedor"
  default     = 8000
}

variable "container_memory_in_mbs" {
  type        = number
  description = "Memoria del contenedor en MB"
  default     = 512
}

variable "container_cpu_count" {
  type        = number
  description = "CPUs del contenedor"
  default     = 1
}

variable "openai_api_key" {
  type        = string
  description = "OpenAI API Key"
  sensitive   = true
}

variable "instagram_email" {
  type        = string
  description = "Email de Instagram Business"
  sensitive   = true
}

variable "instagram_password" {
  type        = string
  description = "Contraseña de aplicación de Instagram"
  sensitive   = true
}

variable "database_password" {
  type        = string
  description = "Contraseña de PostgreSQL"
  sensitive   = true
}

variable "secret_key" {
  type        = string
  description = "Secret Key para sesiones"
  sensitive   = true
}

variable "cors_origins" {
  type        = string
  description = "CORS origins permitidos"
  default     = "http://localhost:3000,https://tu-dominio.com"
}

variable "tags" {
  type = map(string)
  description = "Tags para recursos"
  default = {
    Project     = "BBVA-Seguros"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
