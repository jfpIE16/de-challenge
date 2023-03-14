# Setup container to run Airflow

docker-spin-up:
	docker compose up airflow-init && docker compose up --build -d

perms:
	sudo mkdir -p logs plugins temp dags tests migrations && sudo chmod -R u=rwx,g=rwx,o=rwx logs plugins temp dags tests migrations

up: perms docker-spin-up warehouse-migration

down:
	docker compose down

sh:
	docker exec -ti webserver bash

# Testing, auto formatting, type & lint checks

format:
	docker exec webserver python -m black -S --line-length 79 .

isort:
	docker exec webserver isort .

type:
	docker exec webserver mypy --ignore-missing-imports /opt/airflow

lint:
	docker exec webserver flake8 /opt/airflow/dags

ci: isort format type lint

# Setup cloud infrastructure

tf-init:
	terraform -chdir=./terraform init

infra-up:
	terraform -chdir=./terraform apply

infra-down:
	terraform -chdir=./terraform destroy

infra-config:
	terraform -chdir=./terraform output

# Manage DB migrations

db-migration:
	@read -p "Enter migration name": migration_name; docker exec webserver yoyo new ./migrations -m "$$migration_name"

warehouse-migration:
	docker exec webserver yoyo develop --no-config-file --database postgres://fernando:ferpassword1234@warehouse:5432/door2door ./migrations

warehouse-rollback:
	docker exec webserver yoyo rollback --no-config-file --database postgres://fernando:ferpassword1234@warehouse:5432/door2door ./migrations

# Port forwarding from cloud to Local machine

cloud-airflow:
	terraform -chdir=./terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i private_key.pem ubuntu@$$(terraform -chdir=./terraform output -raw ec2_public_dns) -N -f -L 8888:$$(terraform -chdir=./terraform output -raw ec2_public_dns):8080 && xdg-open http://localhost:8888 && rm private_key.pem

# Helpers

ssh-ec2:
	terraform -chdir=./terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -i private_key.pem ubuntu@$$(terraform -chdir=./terraform output -raw ec2_public_dns) && rm private_key.pem
