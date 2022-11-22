variable "name" {
  description = "Name of this service"
  type        = string
}

variable "gcp_project" {
  description = "Google Cloud project where all resources are located"
  type        = string
}

variable "gcp_region" {
  description = "Google Cloud region where all resources are located"
  type        = string
}

variable "gcp_zone" {
  description = "Google Cloud zone where all zonal resources are located"
  type        = string
}

variable "managed_zone_name" {
  description = "Name of the DNS managed zone that has already been provisioned"
  type        = string
}

variable "domain" {
  description = "Domain to be managed by the DNS"
  type        = string
}

variable "cloudrun_service_name" {
  description = "The name of the Cloud Run service to be routed to"
  type        = string
}

variable "storage_home_name" {
  description = "Name of Google Cloud Storage bucket resource for website homepage"
  type        = string
}

variable "storage_frontend_name" {
  description = "Name of Google Cloud Storage bucket resource for website frontend"
  type        = string
}

variable "production_buckets" {
  description = "Specifications for buckets to be routed in production"
  type        = map(object({ bucket_name=string, enable_cdn=bool, paths=list(string) }))
}

variable "staging_buckets" {
  description = "Specifications for buckets to be routed in staging"
  type        = map(object({ bucket_name=string, enable_cdn=bool, paths=list(string) }))
}

variable "dns_additional_records" {
  description = "Additional DNS A records for the zone"
  type        = map(string)
}