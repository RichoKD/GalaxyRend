variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
}

variable "backend_image" {
  description = "Docker image URL for the backend service"
  type        = string
}

variable "frontend_image" {
  description = "Docker image URL for the frontend service"
  type        = string
}

variable "worker_image" {
  description = "Docker image URL for the worker service"
  type        = string
}
