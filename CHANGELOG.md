## 1.0.1 (2022-09-29)

### Refactor

- refactor: fix refs to envidat, docs with correct port, doc format
- update ALLOWED_HOSTS if DEBUG=True, then from env in production
- move django files to monitoring-api subdir
- prep move django files to subdir, get DEBUG setting from env
- remove nginx waitress confix and separate run_server file
