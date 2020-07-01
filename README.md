# web-authenticator
Authenticate a user against a local database and then request an API key from Elasticsearch with the proper profile to provide the user with the rights required.

### Initial DB seed

cat ./initial.sql | podman exec -it <container-name> psql -U <user> -d <database>
