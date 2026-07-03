rm -R -f ./migrations && psql -h localhost -U FMA_CoexCA03 -d FMA_CoexCA03-Meteorological -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

psql -h localhost -U FMA_CoexCA03 -d FMA_CoexCA03-Meteorological -c 'CREATE EXTENSION unaccent;' && pipenv run flask db init && pipenv run flask db migrate -m "Initial migration" && pipenv run flask db upgrade
