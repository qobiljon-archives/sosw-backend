set -a
source .env
set +a
exec sudo docker logs sosw-api-server --follow