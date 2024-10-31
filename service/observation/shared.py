from typing import List

OBSERVATION_HEADERS: List[str] = ["id","resource_type","status","patient_id"]

def get_observation_url(patient_id: str) -> str:
    return f"https://hapi.fhir.org/baseR5/Observation?subject=patient%2F{patient_id}"

OBSERVATION_TABLE_TEMP_NAME = "observation_temp"
CREATE_OBSERVATION_TABLE_PRODUCTION: List[str] = [
    (
        'CREATE TABLE IF NOT EXISTS public.observation('
        ' id character varying COLLATE pg_catalog."default" NOT NULL,'
        ' resource_type character varying COLLATE pg_catalog."default" NOT NULL,'
        ' status character varying COLLATE pg_catalog."default" NOT NULL,'
        ' patient_id character varying COLLATE pg_catalog."default" NOT NULL,'
        ' CONSTRAINT observation_pkey PRIMARY KEY (id),'
        ' CONSTRAINT observation_patient_id_fkey FOREIGN KEY (patient_id)'
        '  REFERENCES public.patient (id) MATCH SIMPLE'
        '  ON UPDATE NO ACTION'
        '  ON DELETE NO ACTION)'
    ),
    'ALTER TABLE IF EXISTS public.observation OWNER to bochap;',
]

CREATE_OBSERVATION_TABLE_TEMP: str = (
    'CREATE TEMP TABLE IF NOT EXISTS observation_temp ('
    ' id character varying COLLATE pg_catalog."default" NOT NULL,'
    ' resource_type character varying COLLATE pg_catalog."default" NOT NULL,'
    ' status character varying COLLATE pg_catalog."default" NOT NULL,'
    ' patient_id character varying COLLATE pg_catalog."default" NOT NULL,'
    ' CONSTRAINT observation_temp_pkey PRIMARY KEY (id))'
)

MERGE_OBSERVATION_TABLE_TEMP_TO_TABLE_PRODUCTION: str = (
    'MERGE INTO observation o'
    ' USING observation_temp t'
    ' ON (t.id = o.id)'
    ' WHEN MATCHED THEN'
    '  UPDATE SET'
    '    resource_type = t.resource_type,'
    '    status = t.status,'
    '    patient_id = t.patient_id'
    ' WHEN NOT MATCHED THEN'
    '  INSERT (id, resource_type, status, patient_id) VALUES (t.id, t.resource_type, t.status, t.patient_id)'
)

TRUNCATE_OBSERVATION_TABLE_TEMP: str = 'TRUNCATE TABLE observation_temp;'