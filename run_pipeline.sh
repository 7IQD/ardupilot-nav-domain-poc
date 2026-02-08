#!/bin/bash
set -e

echo "🧹 STEP 1 — Clean old state"
rm -f bin/nav_domain.db
rm -rf bin/vault/vault_*/*
rm -rf bin/vault/warehouse/*
rm -rf bin/vault/gold/*

echo "🏗️ STEP 2 — Initialize vault structure"
python3 -m src.core.initialize_db

echo "🚀 STEP 3 — Start Engine-1 (Live ingest)"
python3 -m src.runner.main


