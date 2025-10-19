# Data Engineering Stack dengan Docker Compose

Stack ini berisi semua komponen yang diperlukan untuk data engineering:

## Komponen yang Tersedia

- **Apache NiFi 1.25.0** - Data ingestion dan processing
- **Apache Airflow 2.7.3** - Workflow orchestration
- **Elasticsearch 8.11.0** - Search dan analytics engine
- **Kibana 8.11.0** - Data visualization
- **PostgreSQL 15** - Database utama
- **pgAdmin 4 7.4** - Database administration

## Port yang Digunakan

- **8080** - Apache NiFi
- **8081** - Apache Airflow Web UI
- **5601** - Kibana
- **9200** - Elasticsearch
- **5432** - PostgreSQL
- **8080** - pgAdmin (akan conflict dengan NiFi, gunakan port 8080 untuk NiFi)

## Cara Menjalankan

1. **Clone atau download project ini**

2. **Buat direktori yang diperlukan:**
```bash
mkdir -p dags logs plugins
```

3. **Jalankan semua service:**
```bash
docker-compose up -d
```

4. **Akses aplikasi:**
   - NiFi: http://localhost:8080/nifi
   - Airflow: http://localhost:8081 (admin/admin)
   - Kibana: http://localhost:5601
   - pgAdmin: http://localhost:8080 (admin@admin.com/admin)

## Catatan Penting

- **Konflik Port**: NiFi dan pgAdmin sama-sama menggunakan port 8080. Untuk mengatasi ini, Anda bisa:
  - Mengubah port pgAdmin di docker-compose.yml
  - Atau mengakses pgAdmin melalui port yang berbeda

- **Memory Requirements**: Pastikan sistem Anda memiliki minimal 8GB RAM untuk menjalankan semua service

- **Data Persistence**: Semua data disimpan dalam Docker volumes dan akan bertahan meskipun container di-restart

## Troubleshooting

Jika ada masalah dengan Airflow, jalankan:
```bash
docker-compose run --rm airflow-init
```

Untuk melihat logs:
```bash
docker-compose logs -f [service-name]
```

## Versi Kompatibel

Semua versi telah dipilih untuk kompatibilitas maksimal:
- PostgreSQL 15 dengan Airflow 2.7.3
- Elasticsearch 8.11.0 dengan Kibana 8.11.0
- NiFi 1.25.0 dengan Zookeeper 7.4.0
- Redis 7.2 untuk Airflow Celery executor
