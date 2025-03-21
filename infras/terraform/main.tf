terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.80.0"
    }
  }
}

// The library with methods for creating and
// managing the infrastructure in GCP, this will
// apply to all the resources in the project
provider "google" {
  credentials = "./secrets/fine-ring-448014-h4-9e4bab6121f5.json"
  project     = var.project_id
  region      = var.region
}

// Google Kubernetes Engine
resource "google_container_cluster" "emotiai-cluster" {
  name = "${var.project_id}-emotiai-gke"
  location = var.zone
  remove_default_node_pool = true 
  initial_node_count = 1
}

// Node pool: a group of VMs within the cluster, 
// and you can have multiple node pools with different configurations in the same cluster.
resource "google_container_node_pool" "emotiai-nodes" {
  name = "emotiai-node-pool"
  location = var.zone
  cluster = google_container_cluster.emotiai-cluster.name
  node_count = 2
  
  node_config {
    preemptible = true # similar to spot VMs 
    machine_type = var.machine_type
    disk_size_gb = var.boot_disk_size
  }

  # autoscaling {
  #   min_node_count = 1
  #   max_node_count = 3
  # }
}

# resource "google_compute_firewall" "sgd-firewall" {
#   name = var.firewall_name
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports = ["30001"]
#   }

#   source_ranges = ["0.0.0.0/0"] // Allow all traffic
# }