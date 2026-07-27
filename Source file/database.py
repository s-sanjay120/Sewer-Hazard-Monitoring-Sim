from data_store import DATABASE_PATH, initialize_database, sync_sensor_log


initialize_database()
new_readings = sync_sensor_log()

print(f"Database ready at {DATABASE_PATH}")
print(f"Added {new_readings} new sensor readings")
