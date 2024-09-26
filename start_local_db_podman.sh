# Build the Docker image
podman build -t my-postgres-image ./artifacts/images/postgres
podman run -d --name business-db -p 5432:5432 my-postgres-image

# Wait for the PostgreSQL server to be ready
until podman exec business-db pg_isready; do sleep 3; done


echo "Applying db schema updates"
yoyo apply artifacts/migrations

