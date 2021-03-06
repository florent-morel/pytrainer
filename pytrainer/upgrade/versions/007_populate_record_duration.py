from pytrainer.upgrade.context import UPGRADE_CONTEXT
from sqlalchemy.sql.expression import text
import logging
import sqlalchemy

# record duration added in version 1.8.0

def upgrade(migrate_engine=None):
    if migrate_engine is None:
        # sqlalchemy-migrate 0.5.4 does not provide migrate engine to upgrade scripts
        migrate_engine = sqlalchemy.create_engine(UPGRADE_CONTEXT.db_url)
    logging.info("Populating records.duration column")
    records = migrate_engine.execute("select id_record, time from records where duration is null")
    for record in records:
        record_id = record["id_record"]
        record_time = record["time"]
        try:
            duration = int(record_time)
        except:
            logging.info("Error parsing time (%s) as int for record_id: %s" % (record_time, record_id))
            duration = 0
        logging.debug("setting record %s duration to %d" , record_id, duration)
        migrate_engine.execute(text("update records set duration=:duration where id_record=:record_id"), duration=duration, record_id=record_id)
    records.close()
    
# work around a migrate bug
try:
    import migrate.versioning.exceptions as ex1
    import migrate.changeset.exceptions as ex2
    ex1.MigrateDeprecationWarning = ex2.MigrateDeprecationWarning
except:
    pass
