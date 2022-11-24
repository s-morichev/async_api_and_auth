FROM postgres:15.1-alpine
COPY dump.gz /opt/
RUN gunzip -c /opt/dump.gz > /docker-entrypoint-initdb.d/dump.sql \
    && rm /opt/dump.gz