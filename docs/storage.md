# Storage Backends

DocuCrawler supports a plugin-based storage system. You can switch backends by changing the `storage_type` configuration.

## Local Filesystem (Default)

Saves files to a local directory.

- **Type**: `local`
- **Config**:
  ```yaml
  output: ./downloaded_docs
  ```

## AWS S3

Saves files to an Amazon S3 bucket.

- **Type**: `s3`
- **Requirements**: `pip install docu-crawler[s3]`
- **Config**:
  ```yaml
  storage_type: s3
  s3_bucket: my-docs-bucket
  s3_region: us-east-1
  # Optional: s3_endpoint_url for MinIO/S3-compatible
  ```
- **Credentials**: Standard AWS environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

## Google Cloud Storage (GCS)

Saves files to a GCS bucket.

- **Type**: `gcs`
- **Requirements**: `pip install docu-crawler[gcs]`
- **Config**:
  ```yaml
  storage_type: gcs
  bucket: my-docs-bucket
  project: my-gcp-project
  ```
- **Credentials**: `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to JSON key.

## Azure Blob Storage

Saves files to an Azure Storage container.

- **Type**: `azure`
- **Requirements**: `pip install docu-crawler[azure]`
- **Config**:
  ```yaml
  storage_type: azure
  azure_container: my-docs-container
  ```
- **Credentials**: `AZURE_STORAGE_CONNECTION_STRING` environment variable.

## SFTP

Saves files to a remote server via SFTP.

- **Type**: `sftp`
- **Requirements**: `pip install docu-crawler[sftp]`
- **Config**:
  ```yaml
  storage_type: sftp
  sftp_host: remote.server.com
  sftp_user: username
  sftp_remote_path: /var/www/html/docs
  ```
- **Credentials**: `SFTP_PASSWORD` environment variable or SSH key file (`sftp_key_file` in config).

