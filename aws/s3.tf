resource "aws_s3_bucket" "director_logs_bucket" {
  bucket = "${var.namespace}-director-logs"

  object_lock_enabled = true
}