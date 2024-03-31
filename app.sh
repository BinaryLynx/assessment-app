#!/bin/bash

alembic upgrade head

waitress-serve --call app:app_factory.get_app
