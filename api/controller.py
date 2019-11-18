from app import (
    User,
    user_schema,
    users_schema,
    Reading,
    reading_schema,
    readings_schema,
    db,
)
from flask import request, jsonify, abort
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from datetime import datetime, timedelta
import json


def insert_user(request):
    user_id = request.json["user_id"]
    first_name = request.json["first_name"]
    surname = request.json["surname"]
    email = request.json["email"]
    sensor_id = request.json["sensor_id"]
    username = request.json["username"]

    new_user = User(user_id, first_name, surname, email, sensor_id, username)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify({"Msg": "Username, Sensor ID, Email or User_ID already in use"}),
            400,
        )

    return user_schema.jsonify(new_user), 201


def select_user(username):
    user = User.query.filter_by(username=username).first()
    if json.dumps(user) == "null":
        return {"msg": "user not found"}, 404
    return user_schema.jsonify(user)


def select_all_users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)


def insert_reading(sensor_id):
    db.session.rollback()
    temp_mean = request.json[sensor_id]["temp_mean"]
    pressure_mean = request.json[sensor_id]["pressure_mean"]
    humidity_mean = request.json[sensor_id]["humidity_mean"]
    tvoc_mean = request.json[sensor_id]["tvoc_mean"]

    new_reading = Reading(temp_mean, pressure_mean, humidity_mean, tvoc_mean, sensor_id)

    db.session.add(new_reading)
    db.session.commit()

    return reading_schema.jsonify(new_reading), 201


def select_readings(sensor_id):
    measurement = request.args.get("measurement")
    if (
        measurement != "humidity_mean"
        and measurement != "pressure_mean"
        and measurement != "temp_mean"
        and measurement != "tvoc_mean"
    ):
        return {"msg": "Please ensure you include a valid measurement"}, 400

    lower_limit = request.args.get("lower_limit")[:10] + " 00:00:00"
    upper_limit = request.args.get("upper_limit")[:10] + " 23:59:59"

    lower_limit = datetime.strptime(lower_limit, "%Y-%m-%d %H:%M:%S")
    upper_limit = datetime.strptime(upper_limit, "%Y-%m-%d %H:%M:%S")

    readings_for_sensor = (
        Reading.query.with_entities(getattr(Reading, measurement), Reading.timestamp)
        .filter_by(sensor_id=sensor_id)
        .filter(Reading.timestamp > lower_limit)
        .filter(Reading.timestamp < upper_limit)
    )

    result = readings_schema.dump(readings_for_sensor)

    if not len(result):
        abort(404, "no readings")
        # return {"msg": "no readings found for this sensor ID"}, 404
    return jsonify(result)


def select_most_recent_reading(sensor_id):
    most_recent_reading = (
        Reading.query.filter_by(sensor_id=sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    if not most_recent_reading:
        return {"msg": "no readings found for this sensor ID"}, 404
    return reading_schema.jsonify(most_recent_reading)
