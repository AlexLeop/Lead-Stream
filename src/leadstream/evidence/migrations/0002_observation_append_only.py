from django.db import migrations

FUNCTION_NAME = "leadstream_reject_observation_mutation"
TRIGGER_NAME = "leadstream_observation_append_only"


def create_append_only_trigger(apps, schema_editor):
    del apps
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        f"""
        CREATE OR REPLACE FUNCTION {FUNCTION_NAME}()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'leadstream_observation is append-only';
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS {TRIGGER_NAME} ON leadstream_observation;
        CREATE TRIGGER {TRIGGER_NAME}
        BEFORE UPDATE OR DELETE ON leadstream_observation
        FOR EACH ROW EXECUTE FUNCTION {FUNCTION_NAME}();
        """
    )


def remove_append_only_trigger(apps, schema_editor):
    del apps
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        f"""
        DROP TRIGGER IF EXISTS {TRIGGER_NAME} ON leadstream_observation;
        DROP FUNCTION IF EXISTS {FUNCTION_NAME}();
        """
    )


class Migration(migrations.Migration):
    dependencies = [("evidence", "0001_initial")]

    operations = [
        migrations.RunPython(create_append_only_trigger, remove_append_only_trigger),
    ]
