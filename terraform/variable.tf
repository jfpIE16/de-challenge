## AWS Account level config: region
variable "aws_region" {
    description = "AWS region"
    type        = string
    default     = "us-east-1"
}

## Key to allow connection to our EC2 instance
variable "key_name" {
    description = "EC2 key name"
    type        = string
    default     = "fernando-key"
}

## EC2 instance type
variable "instance_type" {
    description = "Instance type for EC2"
    type        = string
    default     = "m4.large"
}

## Alert email receiver
variable "alert_email_id" {
    description = "Email id to send alerts to "
    type        = string
    default     = "jf23perez@gmail.com"
}

## Repo URL
variable "repo_url" {
    description = "Repository url to clone into production machine"
    type        = string
    default     = "https://github.com/jfpIE16/de-challenge.git"
}

## S3 Lake folders and name
variable "bucket_name" {
    description = "Main bucket name"
    type        = string
    default     = "door2door-lake"
}

variable "s3_folders" {
    description = "Default folders for the different layers of the Data Lake."
    type        = set(string)
    default     = ["raw", "stage", "curated"]
}