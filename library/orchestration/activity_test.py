import pytest
from temporalio.testing import ActivityEnvironment
from library.meta.config import get_env_config
from library.client.factory import get_api_db_client
from library.storage.vault import Vault
from library.orchestration.model import CustomSqlInput
from library.orchestration.activity import CustomSqlActivity

@pytest.mark.asyncio
async def test_custom_sql_activity_success():
    env_config = get_env_config()
    vault = Vault(env_config)
    db = get_api_db_client(vault, env_config.localhost_override)
    activity_environment = ActivityEnvironment()
    activity = CustomSqlActivity(db)
    try:
        input = CustomSqlInput([
            """
            CREATE TABLE IF NOT EXISTS public.test
            (
                id character varying COLLATE pg_catalog."default" NOT NULL,
                value character varying COLLATE pg_catalog."default" NOT NULL,
                CONSTRAINT test_pkey PRIMARY KEY (id)
            )
            """,
            """
            ALTER TABLE IF EXISTS public.test OWNER to bochap;
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_test_value
                ON public.test USING btree
                (value COLLATE pg_catalog."default" ASC NULLS LAST)
                TABLESPACE pg_default;
            """,
            """DROP INDEX IF EXISTS public.ix_test_value;""",
            """DROP TABLE IF EXISTS public.test;""",
        ])
        await activity_environment.run(activity.execute_sql, input)    
    except Exception as ex:
        assert False, f"'CustomSqlActivity' raised an exception {ex}"
        
