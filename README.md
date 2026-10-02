# TruckFlow

TruckFlow is a freight-logistics prototype with a Django REST API and a static frontend. The checked-in API code includes truck/load records, trip matching, route calculations, and profit estimates.

## Requirements

- Python 3
- The packages listed in `requirements.txt`

## Run locally

From this repository directory:

```bash
python -m venv .venv
```

Activate the virtual environment, then install dependencies and start Django:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000>. The API routes are under `/api/`.

## Tests

No automated test suite is currently present. `python manage.py check` performs Django's system checks after dependencies are installed.

## Security status

Do not deploy this prototype publicly in its current state. The API viewsets allow unauthenticated record changes, and the checked-in settings enable debug mode, wildcard hosts, and permissive credentialed CORS. Authentication and production configuration must be addressed before exposure.

## License

No project license is included. Confirm code and asset ownership before choosing one or permitting reuse.