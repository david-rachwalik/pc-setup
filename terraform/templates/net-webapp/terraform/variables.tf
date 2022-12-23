variable "application_name" {
  type        = string
  description = "The name of your application"
  default     = "demo-2627-0550-7643-4857"
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
