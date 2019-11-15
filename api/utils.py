import schedule
import time
from app import User, user_schema, Reading, reading_schema, readings_schema, db, ArchiveReading , archiveReading_schema,archiveReadings_schema
from flask import request, jsonify
from SQLAlchemy import func


def archiveDay(sensor_id):
    temp_mean = Reading.query(func.avg(Reading.temp_mean))
    pressure_mean = Reading.query(func.avg(Reading.pressure_mean))
    humidity_mean = Reading.query(func.avg(Reading.humidity_mean))
    tvoc_mean = Reading.query(func.avg(Reading.temp_mean))

    new_reading = ArchiveReading(temp_mean, pressure_mean, humidity_mean, tvoc_mean, sensor_id)
 
    db.session.add(new_reading)
    db.session.commit()

    return archiveReading_schema.jsonify(new_reading), 201
        
