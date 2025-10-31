# Makefile para comandos comunes de Kubernetes
# Uso en PowerShell: usar los scripts en /scripts directamente

.PHONY: help deploy status logs clean build-push preflight

help:
	@echo "Comandos disponibles:"
	@echo "  make deploy         - Despliega todo al cluster"
	@echo "  make status         - Muestra el estado actual"
	@echo "  make logs          - Muestra logs de la API"
	@echo "  make clean         - Elimina todos los recursos"
	@echo "  make build-push    - Construye y sube imagen Docker"
	@echo "  make preflight     - Verifica configuración"

deploy:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/postgres.yaml
	kubectl apply -f k8s/minio.yaml
	kubectl apply -f k8s/rabbitmq.yaml
	kubectl wait --for=condition=ready pod -l app=postgres -n file-service --timeout=300s
	kubectl wait --for=condition=ready pod -l app=minio -n file-service --timeout=300s
	kubectl wait --for=condition=ready pod -l app=rabbitmq -n file-service --timeout=300s
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/hpa.yaml
	kubectl apply -f k8s/ingress.yaml
	@echo ""
	@echo "Despliegue completado! Ver estado con: make status"

status:
	@echo "=== Pods ==="
	kubectl get pods -n file-service
	@echo ""
	@echo "=== Services ==="
	kubectl get svc -n file-service
	@echo ""
	@echo "=== Ingress ==="
	kubectl get ingress -n file-service
	@echo ""
	@echo "=== HPA ==="
	kubectl get hpa -n file-service

logs:
	kubectl logs -l app=file-service-api -n file-service -f

clean:
	kubectl delete namespace file-service

build-push:
	docker build -t johannvasquez/file-service:latest .
	docker push johannvasquez/file-service:latest

preflight:
	@echo "Verificando kubectl..."
	@kubectl version --client
	@echo ""
	@echo "Verificando conexión al cluster..."
	@kubectl cluster-info
	@echo ""
	@echo "Verificando nodos..."
	@kubectl get nodes
