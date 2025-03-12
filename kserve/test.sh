#!/bin/bash
curl -H "Content-Type: application/json" -X POST http://localhost:8080/v1/models/mlp-model:predict -d @./input.json