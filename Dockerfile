FROM python:3.7

COPY . /opt/voucher_selection
RUN cd /opt/voucher_selection && \
    pip install --use-feature=in-tree-build -e .

# Required parameters
ENV APP_DB_USERNAME=
ENV APP_DB_PASSWORD=
ENV APP_DB_HOST=

ENV APP_SERVER_HOST=0.0.0.0
ENV APP_SERVER_PORT=8080

EXPOSE 8080
CMD ["voucher_selection", "api", "run"]
