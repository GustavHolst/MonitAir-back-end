from app import User, user_schema, Reading, reading_schema, readings_schema, db
from flask import request, jsonify


def insert_user(request):
    first_name = request.json["first_name"]
    surname = request.json["surname"]
    email = request.json["email"]
    sensor_id = request.json["sensor_id"]
    username = request.json["username"]

    new_user = User(first_name, surname, email, sensor_id, username)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


def select_user(username):
    user = User.query.filter_by(username=username).first()
    return user_schema.jsonify(user)


def insert_reading(sensor_id):
    temp_mean = request.json[sensor_id]["temp_mean"]
    pressure_mean = request.json[sensor_id]["pressure_mean"]
    humidity_mean = request.json[sensor_id]["humidity_mean"]
    tvoc_mean = request.json[sensor_id]["tvoc_mean"]
    gas_baseline = request.json[sensor_id]["gas_baseline"]
    baseline_temp = request.json[sensor_id]["baseline_temp"]

    new_reading = Reading(
        temp_mean,
        pressure_mean,
        humidity_mean,
        tvoc_mean,
        sensor_id,
        baseline_temp,
        gas_baseline,
    )

    db.session.add(new_reading)
    db.session.commit()

    print(new_reading)
    return reading_schema.jsonify(new_reading), 201


def select_readings(sensor_id):
    all_readings_for_sensor = Reading.query.filter_by(sensor_id=sensor_id).limit(8640)
    result = readings_schema.dump(all_readings_for_sensor)
    return jsonify(result)


def select_most_recent_reading(sensor_id):
    most_recent_reading = (
        Reading.query.filter_by(sensor_id=sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    return reading_schema.jsonify(most_recent_reading)
