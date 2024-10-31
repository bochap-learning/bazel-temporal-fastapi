    """
    https://fhir.hl7.at/r5-core-main/StructureDefinition-at-core-patient.profile.json.html
    https://darrendevitt.com/getting-pagination-in-fhir-wrong-is-a-rite-of-passage/
    https://chat.fhir.org/#narrow/stream/179166-implementers/topic/_count.20and.20CapabilityStatements
    https://www.devdays.com/wp-content/uploads/2021/12/DD21US_20210608_Sloan_Holiday_Lessons_learned_with_Fhir_Paging_and_with_Plain_ServerFa_ade_Fhir_Servers_and_Load_Balanced_Systems_.pdf

    https://hapi.fhir.org/baseR5/Patient?address-postalcode=02718&_getpagesoffset=10&_count=10
    """


Census Data
https://proximityone.com/zip16dp1.htm
https://facts.usps.com/42000-zip-codes/


docker compose -f docker-api-db.yml up -d 

curl "http://localhost:9000/bochap/observation-4965.csv" 

COPY patients (id, first_name, gender, birth_date)
FROM PROGRAM 'curl "http://minio:9000/public-bucket/patients.csv"'
WITH (FORMAT CSV, HEADER TRUE);



-- Table: public.patients

-- DROP TABLE IF EXISTS public.patients;

CREATE TABLE IF NOT EXISTS public.patients
(
    id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    first_name character varying(255) COLLATE pg_catalog."default",
    gender character varying(50) COLLATE pg_catalog."default",
    birth_date character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT patients_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.patients
    OWNER to bochap;

bazel build //service/patient:service_rdbms


CREATE TABLE greetings WITH (
    'connector' = 'kafka',
    'topic' = 'greetings',
    'format' = 'json',
    'properties.bootstrap.servers' = 'csgh6eu7lc8s5d75qjcg.any.us-east-1.mpx.prd.cloud.redpanda.com:9092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'properties.security.protocol' = 'SASL_SSL',
    'properties.sasl.mechanism' = 'SCRAM-SHA-256',
    'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.scram.ScramLoginModule required password="1234qwer" username="myuser";'
) AS
SELECT
    CONCAT('Hello, ', name) as greeting,
    PROCTIME() as processing_time
FROM
    names;

  SELECT
    name,
    website
FROM names;   


CREATE TABLE names (name VARCHAR, website VARCHAR) WITH (
    'connector' = 'kafka',
    'topic' = 'names',
    'format' = 'json',
    'properties.bootstrap.servers' = 'csgh6eu7lc8s5d75qjcg.any.us-east-1.mpx.prd.cloud.redpanda.com:9092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'properties.security.protocol' = 'SASL_SSL',
    'properties.sasl.mechanism' = 'SCRAM-SHA-256',
    'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.scram.ScramLoginModule required password="rC%33T.gl;pU-9HZI6v|" username="bochap";'
);