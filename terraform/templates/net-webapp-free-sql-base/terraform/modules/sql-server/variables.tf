variable "resource_group" {
  type        = string
  description = "The resource group"
  default     = ""
}

variable "application_name" {
  type        = string
  description = "The name of your application"
  default     = ""
}

variable "environment" {
  type        = string
  description = "The environment (dev, test, prod...)"
  default     = "dev"
}

variable "location" {
  type        = string
  description = "The Azure region where all resources in this example should be created"
  default     = ""
}

variable "administrator_login" {
  type        = string
  description = "The SQL Server administrator login"
  default     = "sqladmin"
}

variable "sku_name" {
  type        = string
  description = "The SKU name for SQL Database"
  default     = "Free"
}
