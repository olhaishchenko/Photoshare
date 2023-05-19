# Photoshare
application with images

## Dev
For running locally use dev: `uvicorn main:contact_app --reload`
Before merging a PR, please check that application at least starting.

## Migrations
```sh
alembic revision --autogenerate -m '<Your Description>'
alembic upgrade head
```

If you got new migrations after pull:
```sh
alembic upgrade head
```

