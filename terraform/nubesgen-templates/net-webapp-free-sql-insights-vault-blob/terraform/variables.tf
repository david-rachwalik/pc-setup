variable "application_name" {
  type        = string
  description = "The name of your application"
  default     = "net-webapp-free-sql-insights-vault-blob"
}

variable "environment" {
  type        = string
  description = "The environment (dev, test, prod...)"
  default     = ""
}

variable "location" {
  type        = string
  description = "The Azure region where all resources in this example should be created"
  default     = "centralus"
}
