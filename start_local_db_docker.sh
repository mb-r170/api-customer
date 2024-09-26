# Build the Docker image
docker build -t my-postgres-image ./artifacts/images/postgres
docker run -d --name business-db -p 5432:5432 my-postgres-image

# Wait for the PostgreSQL server to be ready
until docker exec business-db pg_isready; do sleep 3; done


echo "Applying db schema updates"
yoyo apply artifacts/migrations

