from app.config import Settings


def test_render_postgres_url_is_normalized_for_asyncpg():
    settings = Settings(_env_file=None, database_url="postgres://u:p@db.example:5432/app")
    assert settings.database_url_async == "postgresql+asyncpg://u:p@db.example:5432/app"


def test_sslmode_is_translated_to_asyncpg_ssl_parameter():
    settings = Settings(_env_file=None, database_url="postgresql://u:p@db.example/app?sslmode=require")
    assert settings.database_url_async.endswith("?ssl=require")


def test_admin_ids_are_parsed_from_csv():
    settings = Settings(_env_file=None, admin_ids="123, 456")
    assert settings.admin_id_set == frozenset({123, 456})
