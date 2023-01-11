# EnviDat Monitoring Backend Chart

Chart for EnviDat Monitoring Backend in Django.

- Interfaces with production database.
- Can autoscale with load.

## Secrets

Requires secrets to be pre-populated.

- **monitoring-api-vars** prod db creds, django variables

  - key: SECRET_KEY  (random, for Django)
  - key: ALLOWED_HOSTS  (server to access from)
  - key: PROXY_PREFIX  (url prefix, if behind proxy)
  - key: LOG_LEVEL
  - key: PORT
  - key: DATABASE_NAME
  - key: DATABASE_USER
  - key: DATABASE_PASSWORD
  - key: DATABASE_HOST
  - key: DATABASE_PORT

  ```bash
  kubectl create secret generic monitoring-api-vars \
  --from-literal=SECRET_KEY=xxxxxxx \
  --from-literal=ALLOWED_HOSTS='["envidat.ch", "monitoring.envidat.ch"]' \
  --from-literal=PROXY_PREFIX=/data-api \
  --from-literal=LOG_LEVEL=DEBUG \
  --from-literal=DATABASE_NAME=xxxxxxx \
  --from-literal=DATABASE_USER=xxxxxxx \
  --from-literal=DATABASE_PASSWORD=xxxxxxx \
  --from-literal=DATABASE_HOST=xxxxxxx \
  --from-literal=DATABASE_PORT=xxxxxxx
  ```

- **monitoring-lwf-vars** lwf db creds

  - key: LWF_DB_SCHEMA  (format: '-c search_path=<SCHEMA>')
  - key: LWF_DB_NAME
  - key: LWF_DB_USER
  - key: LWF_DB_PASSWORD
  - key: LWF_DB_HOST
  - key: LWF_DB_PORT

  ```bash
  kubectl create secret generic monitoring-lwf-vars \
  --from-literal=LWF_DB_SCHEMA='-c search_path=lwf' \
  --from-literal=LWF_DB_NAME=xxxxxxx \
  --from-literal=LWF_DB_USER=xxxxxxx \
  --from-literal=LWF_DB_PASSWORD=xxxxxxx \
  --from-literal=LWF_DB_HOST=xxxxxxx \
  --from-literal=LWF_DB_PORT=xxxxxxx
  ```

- **monitoring-gcnet-vars** gcnet db creds

  - key: GCNET_DB_SCHEMA  (format: '-c search_path=<SCHEMA>')
  - key: GCNET_DB_NAME
  - key: GCNET_DB_USER
  - key: GCNET_DB_PASSWORD
  - key: GCNET_DB_HOST
  - key: GCNET_DB_PORT

  ```bash
  kubectl create secret generic monitoring-gcnet-vars \
  --from-literal=GCNET_DB_SCHEMA='-c search_path=gcnet' \
  --from-literal=GCNET_DB_NAME=xxxxxxx \
  --from-literal=GCNET_DB_USER=xxxxxxx \
  --from-literal=GCNET_DB_PASSWORD=xxxxxxx \
  --from-literal=GCNET_DB_HOST=xxxxxxx \
  --from-literal=GCNET_DB_PORT=xxxxxxx
  ```

- **envidat-star** for https / tls certs

  - Standard Kubernetes TLS secret for \*.envidat.ch

## Deployment

```shell
helm upgrade --install monitoring-api oci://registry.envidat.ch/envidat/
monitoring-api --namespace envidat
```
