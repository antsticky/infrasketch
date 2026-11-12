"""Services that belong to neither Azure nor AWS.

Each class is a node. The icon browser groups them by category.
Add another the same way: a class here, an SVG under
``data/icons/external/``, and a row in ``data/external-catalog.json``.
"""

from infrasketch.model import Node

__all__ = [
    "Akamai",
    "ApacheKafka",
    "ArangoDB",
    "ArgoCD",
    "Auth0",
    "Bitbucket",
    "Bunny",
    "Cassandra",
    "CircleCI",
    "ClickHouse",
    "Cloudflare",
    "CockroachDB",
    "CouchDB",
    "Couchbase",
    "Databricks",
    "Datadog",
    "Docker",
    "DuckDB",
    "Dynatrace",
    "Elasticsearch",
    "Fastly",
    "Fortinet",
    "GitHub",
    "GitLab",
    "Grafana",
    "Helm",
    "InfluxDB",
    "Jenkins",
    "Jira",
    "Kubernetes",
    "MariaDB",
    "MongoDB",
    "MySQL",
    "NATS",
    "Neo4j",
    "NewRelic",
    "Okta",
    "OpenSearch",
    "OpenShift",
    "PaloAltoNetworks",
    "PostgreSQL",
    "Prometheus",
    "RabbitMQ",
    "Rancher",
    "Redis",
    "SQLite",
    "ScyllaDB",
    "SingleStore",
    "Snowflake",
    "Splunk",
    "TimescaleDB",
    "TravisCI",
]

class GitHub(Node):
    """GitHub."""

    icon = "external/github.svg"
    service = "GitHub"

class GitLab(Node):
    """GitLab."""

    icon = "external/gitlab.svg"
    service = "GitLab"

class Bitbucket(Node):
    """Bitbucket."""

    icon = "external/bitbucket.svg"
    service = "Bitbucket"

class Jenkins(Node):
    """Jenkins."""

    icon = "external/jenkins.svg"
    service = "Jenkins"

class CircleCI(Node):
    """CircleCI."""

    icon = "external/circleci.svg"
    service = "CircleCI"

class TravisCI(Node):
    """Travis CI."""

    icon = "external/travisci.svg"
    service = "Travis CI"

class ArgoCD(Node):
    """Argo CD."""

    icon = "external/argocd.svg"
    service = "Argo CD"

class Cloudflare(Node):
    """Cloudflare."""

    icon = "external/cloudflare.svg"
    service = "Cloudflare"

class Akamai(Node):
    """Akamai."""

    icon = "external/akamai.svg"
    service = "Akamai"

class Fastly(Node):
    """Fastly."""

    icon = "external/fastly.svg"
    service = "Fastly"

class Bunny(Node):
    """Bunny.net."""

    icon = "external/bunny.svg"
    service = "Bunny.net"

class Kubernetes(Node):
    """Kubernetes."""

    icon = "external/kubernetes.svg"
    service = "Kubernetes"

class Docker(Node):
    """Docker."""

    icon = "external/docker.svg"
    service = "Docker"

class Rancher(Node):
    """Rancher."""

    icon = "external/rancher.svg"
    service = "Rancher"

class OpenShift(Node):
    """Red Hat OpenShift."""

    icon = "external/openshift.svg"
    service = "Red Hat OpenShift"

class Helm(Node):
    """Helm."""

    icon = "external/helm.svg"
    service = "Helm"

class Datadog(Node):
    """Datadog."""

    icon = "external/datadog.svg"
    service = "Datadog"

class NewRelic(Node):
    """New Relic."""

    icon = "external/newrelic.svg"
    service = "New Relic"

class Grafana(Node):
    """Grafana."""

    icon = "external/grafana.svg"
    service = "Grafana"

class Prometheus(Node):
    """Prometheus."""

    icon = "external/prometheus.svg"
    service = "Prometheus"

class Dynatrace(Node):
    """Dynatrace."""

    icon = "external/dynatrace.svg"
    service = "Dynatrace"

class Splunk(Node):
    """Splunk."""

    icon = "external/splunk.svg"
    service = "Splunk"

class Okta(Node):
    """Okta."""

    icon = "external/okta.svg"
    service = "Okta"

class Auth0(Node):
    """Auth0."""

    icon = "external/auth0.svg"
    service = "Auth0"

class PaloAltoNetworks(Node):
    """Palo Alto Networks."""

    icon = "external/palo-alto.svg"
    service = "Palo Alto Networks"

class Fortinet(Node):
    """Fortinet."""

    icon = "external/fortinet.svg"
    service = "Fortinet"

class ApacheKafka(Node):
    """Apache Kafka."""

    icon = "external/kafka.svg"
    service = "Apache Kafka"

class RabbitMQ(Node):
    """RabbitMQ."""

    icon = "external/rabbitmq.svg"
    service = "RabbitMQ"

class NATS(Node):
    """NATS."""

    icon = "external/nats.svg"
    service = "NATS"

class MongoDB(Node):
    """MongoDB."""

    icon = "external/mongodb.svg"
    service = "MongoDB"

class PostgreSQL(Node):
    """PostgreSQL."""

    icon = "external/postgresql.svg"
    service = "PostgreSQL"

class MySQL(Node):
    """MySQL."""

    icon = "external/mysql.svg"
    service = "MySQL"

class Redis(Node):
    """Redis."""

    icon = "external/redis.svg"
    service = "Redis"

class Elasticsearch(Node):
    """Elasticsearch."""

    icon = "external/elasticsearch.svg"
    service = "Elasticsearch"

class Cassandra(Node):
    """Cassandra."""

    icon = "external/cassandra.svg"
    service = "Cassandra"

class MariaDB(Node):
    """MariaDB."""

    icon = "external/mariadb.svg"
    service = "MariaDB"

class SQLite(Node):
    """SQLite."""

    icon = "external/sqlite.svg"
    service = "SQLite"

class Neo4j(Node):
    """Neo4j."""

    icon = "external/neo4j.svg"
    service = "Neo4j"

class Couchbase(Node):
    """Couchbase."""

    icon = "external/couchbase.svg"
    service = "Couchbase"

class CouchDB(Node):
    """CouchDB."""

    icon = "external/couchdb.svg"
    service = "CouchDB"

class InfluxDB(Node):
    """InfluxDB."""

    icon = "external/influxdb.svg"
    service = "InfluxDB"

class CockroachDB(Node):
    """CockroachDB."""

    icon = "external/cockroachdb.svg"
    service = "CockroachDB"

class ClickHouse(Node):
    """ClickHouse."""

    icon = "external/clickhouse.svg"
    service = "ClickHouse"

class ScyllaDB(Node):
    """ScyllaDB."""

    icon = "external/scylladb.svg"
    service = "ScyllaDB"

class OpenSearch(Node):
    """OpenSearch."""

    icon = "external/opensearch.svg"
    service = "OpenSearch"

class DuckDB(Node):
    """DuckDB."""

    icon = "external/duckdb.svg"
    service = "DuckDB"

class TimescaleDB(Node):
    """TimescaleDB."""

    icon = "external/timescaledb.svg"
    service = "TimescaleDB"

class ArangoDB(Node):
    """ArangoDB."""

    icon = "external/arangodb.svg"
    service = "ArangoDB"

class SingleStore(Node):
    """SingleStore."""

    icon = "external/singlestore.svg"
    service = "SingleStore"

class Snowflake(Node):
    """Snowflake."""

    icon = "external/snowflake.svg"
    service = "Snowflake"

class Databricks(Node):
    """Databricks."""

    icon = "external/databricks.svg"
    service = "Databricks"

class Jira(Node):
    """Atlassian Jira."""

    icon = "external/jira.svg"
    service = "Atlassian Jira"

EXTERNAL_CREDITS = {
    "external/github.svg": "GitHub mark © GitHub",
    "external/gitlab.svg": "GitLab mark © GitLab",
    "external/bitbucket.svg": "Bitbucket mark © Bitbucket",
    "external/jenkins.svg": "Jenkins mark © Jenkins",
    "external/circleci.svg": "CircleCI mark © CircleCI",
    "external/travisci.svg": "Travis CI mark © Travis CI",
    "external/argocd.svg": "Argo CD mark © Argo CD",
    "external/cloudflare.svg": "Cloudflare mark © Cloudflare",
    "external/akamai.svg": "Akamai mark © Akamai",
    "external/fastly.svg": "Fastly mark © Fastly",
    "external/bunny.svg": "Bunny.net mark © Bunny.net",
    "external/kubernetes.svg": "Kubernetes mark © Kubernetes",
    "external/docker.svg": "Docker mark © Docker",
    "external/rancher.svg": "Rancher mark © Rancher",
    "external/openshift.svg": "Red Hat OpenShift mark © Red Hat OpenShift",
    "external/helm.svg": "Helm mark © Helm",
    "external/datadog.svg": "Datadog mark © Datadog",
    "external/newrelic.svg": "New Relic mark © New Relic",
    "external/grafana.svg": "Grafana mark © Grafana",
    "external/prometheus.svg": "Prometheus mark © Prometheus",
    "external/dynatrace.svg": "Dynatrace mark © Dynatrace",
    "external/splunk.svg": "Splunk mark © Splunk",
    "external/okta.svg": "Okta mark © Okta",
    "external/auth0.svg": "Auth0 mark © Auth0",
    "external/palo-alto.svg": "Palo Alto Networks mark © Palo Alto Networks",
    "external/fortinet.svg": "Fortinet mark © Fortinet",
    "external/kafka.svg": "Apache Kafka mark © Apache Kafka",
    "external/rabbitmq.svg": "RabbitMQ mark © RabbitMQ",
    "external/nats.svg": "NATS mark © NATS",
    "external/mongodb.svg": "MongoDB mark © MongoDB",
    "external/postgresql.svg": "PostgreSQL mark © PostgreSQL",
    "external/mysql.svg": "MySQL mark © MySQL",
    "external/redis.svg": "Redis mark © Redis",
    "external/elasticsearch.svg": "Elasticsearch mark © Elasticsearch",
    "external/cassandra.svg": "Cassandra mark © Cassandra",
    "external/mariadb.svg": "MariaDB mark © MariaDB",
    "external/sqlite.svg": "SQLite mark © SQLite",
    "external/neo4j.svg": "Neo4j mark © Neo4j",
    "external/couchbase.svg": "Couchbase mark © Couchbase",
    "external/couchdb.svg": "CouchDB mark © CouchDB",
    "external/influxdb.svg": "InfluxDB mark © InfluxDB",
    "external/cockroachdb.svg": "CockroachDB mark © CockroachDB",
    "external/clickhouse.svg": "ClickHouse mark © ClickHouse",
    "external/scylladb.svg": "ScyllaDB mark © ScyllaDB",
    "external/opensearch.svg": "OpenSearch mark © OpenSearch",
    "external/duckdb.svg": "DuckDB mark © DuckDB",
    "external/timescaledb.svg": "TimescaleDB mark © TimescaleDB",
    "external/arangodb.svg": "ArangoDB mark © ArangoDB",
    "external/singlestore.svg": "SingleStore mark © SingleStore",
    "external/snowflake.svg": "Snowflake mark © Snowflake",
    "external/databricks.svg": "Databricks mark © Databricks",
    "external/jira.svg": "Atlassian Jira mark © Atlassian Jira",
}
