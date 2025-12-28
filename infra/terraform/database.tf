# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "main" {
  name                = "galaxyrend-db-${random_id.db_suffix.hex}"
  database_version    = "POSTGRES_15"
  region              = var.region
  deletion_protection = false # Set to true for production

  settings {
    tier = "db-f1-micro" # Use larger tier for production

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
  }
  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "random_id" "db_suffix" {
  byte_length = 4
}

resource "google_sql_database" "database" {
  name     = "galaxyrend_db"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "users" {
  name     = "postgres"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Memorystore (Redis)
resource "google_redis_instance" "cache" {
  name               = "galaxyrend-redis"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  authorized_network = google_compute_network.vpc.id
  connect_mode       = "DIRECT_PEERING"

  redis_version = "REDIS_7_0"

  depends_on = [google_service_networking_connection.private_vpc_connection]
}
