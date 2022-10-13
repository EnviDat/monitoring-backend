## 1.0.6 (2022-10-13)

### Fix

- error handling for writer creating file if not exist, lint/format
- change nginx root up one level for /static in url
- revert nginx config without upstream, set error logging

### Refactor

- remove redundant envidatrepo alias from helm chart
- update gcnet data url from envidatrepo to envicloud s3 bucket
- remove refs to dbpg01.wsl.ch (old), add alias for envidatrepo.wsl.ch
- add additional debug log to gcnet importer urllib
- update chart notation for importers to multiline arg
- remove redundant location block in nginx config
- set default chart liveness probes to off/false
- update nginx proxy probe timeouts from 1 to 5
- update importer deployment commands to main.main, timeouts on probes
- update timeouts on chart liveness and startup probes

## 1.0.5 (2022-10-11)

### Fix

- remove drf-spectacular sidecar

### Refactor

- update swagger and redoc endpoint urls
- added swagger schema endpoints to project/urls.py
- update helm chart, remove importers from api deployment
- fix name issue in helm deployment gcnet --> lwf

## 1.0.4 (2022-10-07)

### Fix

- STATIC_ROOT setting in project settings

### Refactor

- fix helm chart syntax, add probes to importers

## 1.0.3 (2022-10-07)

### Fix

- add postgres-client to docker image for db init checks

## 1.0.2 (2022-10-06)

### Refactor

- remove missed spectacular version in pyproject from drf-spectacular
- remove unused DRF dependency, plus all references in code
- revert re_paths, drf-spectacular save state before removal

### Fix

- log format for importers, remove file handler lwf, blacken, isort
- use re_path for urls to allow slash, add spectacular openapi endpoints (+swagger)

## 1.0.1 (2022-09-29)

### Refactor

- refactor: fix refs to envidat, docs with correct port, doc format
- update ALLOWED_HOSTS if DEBUG=True, then from env in production
- move django files to monitoring-api subdir
- prep move django files to subdir, get DEBUG setting from env
- remove nginx waitress confix and separate run_server file
