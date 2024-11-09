from typing import List

PATIENT_HEADERS: List[str] = ["id","first_name","gender","birth_date"]
PATIENT_TABLE_TEMP_NAME: str = "patient_temp"

def get_patients_url(zipcode: str) -> str:
    # caping count to 50 to reduce the number of data and concurrent access in each workflow
    return f"https://hapi.fhir.org/baseR5/Patient?address-postalcode={zipcode}&_getpagesoffset=0&_count=50"


CREATE_PATIENT_TABLE_PRODUCTION: List[str] = [
    (
        'CREATE TABLE IF NOT EXISTS public.patient('
        ' id character varying COLLATE pg_catalog."default" NOT NULL,'
        ' first_name character varying COLLATE pg_catalog."default" NOT NULL,'
        ' gender character varying COLLATE pg_catalog."default" NOT NULL,'
        ' birth_date character varying COLLATE pg_catalog."default" NOT NULL,'
        ' CONSTRAINT patient_pkey PRIMARY KEY (id))'
    ),
    'ALTER TABLE IF EXISTS public.patient OWNER to bochap;',
    (
        'CREATE INDEX IF NOT EXISTS ix_patient_first_name'
        ' ON public.patient USING btree'
        ' (first_name COLLATE pg_catalog."default" ASC NULLS LAST)'
        ' TABLESPACE pg_default;'
    )
]

CREATE_PATIENT_TABLE_TEMP: str = (
    'CREATE TEMP TABLE IF NOT EXISTS patient_temp ('
    ' id character varying COLLATE pg_catalog."default" NOT NULL,'
    ' first_name character varying COLLATE pg_catalog."default" NOT NULL,'
    ' gender character varying COLLATE pg_catalog."default" NOT NULL,'
    ' birth_date character varying COLLATE pg_catalog."default" NOT NULL,'
    ' CONSTRAINT patient_temp_pkey PRIMARY KEY (id))'
)

MERGE_PATIENT_TABLE_TEMP_TO_TABLE_PRODUCTION: str = (
    'MERGE INTO patient p'
    ' USING patient_temp t'
    ' ON (t.id = p.id)'
    ' WHEN MATCHED THEN'
    '  UPDATE SET'
    '    first_name = t.first_name,'
    '    gender = t.gender,'
    '    birth_date = t.birth_date'
    ' WHEN NOT MATCHED THEN'
    '  INSERT (id, first_name, gender, birth_date) VALUES (t.id, t.first_name, t.gender, t.birth_date)'
)

TRUNCATE_PATIENT_TABLE_TEMP: str = 'TRUNCATE TABLE patient_temp;'