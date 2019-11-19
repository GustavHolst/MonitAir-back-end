from app import (
    User,
    user_schema,
    users_schema,
    Reading,
    reading_schema,
    readings_schema,
    db,
)
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from datetime import datetime, timedelta
import json


def insert_user(request):
    try:
        user_id = request.json["user_id"]
        first_name = request.json["first_name"]
        surname = request.json["surname"]
        email = request.json["email"]
        sensor_id = request.json["sensor_id"]
        username = request.json["username"]

        try:
            new_user = User(user_id, first_name, surname, email, sensor_id, username)
            db.session.add(new_user)
            db.session.commit()
            return user_schema.jsonify(new_user), 201

        except IntegrityError:
            db.session.rollback()
            return {"msg": "Username, Sensor ID, Email or User_ID already in use"}, 400

    except KeyError:
        return {"msg": "Info missing from post user request"}, 400


def select_user(username):
    user = User.query.filter_by(username=username).first()

    if isinstance(user, User):
        return user_schema.jsonify(user)

    return {"msg": "User not found"}, 404


def select_all_users():
    all_users = User.query.all()
    if len(all_users):
        return users_schema.jsonify(all_users)
    return {"msg": "No users in the database"}, 404


def insert_reading(sensor_id):
    db.session.rollback()
    try:
        temp_mean = request.json["temp_mean"]
        pressure_mean = request.json["pressure_mean"]
        humidity_mean = request.json["humidity_mean"]
        total_quality_mean = (100 - request.json["total_quality_mean"]) * 5
        new_reading = Reading(
            round(temp_mean, 2),
            round(pressure_mean),
            round(humidity_mean),
            round(total_quality_mean),
            sensor_id,
        )
        db.session.add(new_reading)
        db.session.commit()

        return reading_schema.jsonify(new_reading), 201

    except KeyError:
        return {"msg": "Info missing from post reading request"}, 400

    except TypeError:
        return {"msg": "Readings provided must be numbers (Int or Float)"}, 400


def select_most_recent_reading(sensor_id):
    most_recent_reading = (
        Reading.query.filter_by(sensor_id=sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    if not most_recent_reading:
        return (
            {"msg": "No readings found for this sensor ID"},
            404,
        )
    return reading_schema.jsonify(most_recent_reading)


def select_readings(sensor_id):
    try:
        measurement = request.args.get("measurement")

        if (
            measurement != "temp_mean"
            and measurement != "pressure_mean"
            and measurement != "humidity_mean"
            and measurement != "total_quality_mean"
        ):
            return (
                {
                    "msg": "Measurement query must be: temp_mean, pressure_mean, humidity_mean or total_quality_mean"
                },
                400,
            )

        lower_limit = request.args.get("lower_limit")[:10] + " 00:00:00"
        upper_limit = request.args.get("upper_limit")[:10] + " 23:59:59"

        lower_limit = datetime.strptime(lower_limit, "%Y-%m-%d %H:%M:%S")
        upper_limit = datetime.strptime(upper_limit, "%Y-%m-%d %H:%M:%S")

        readings_for_sensor = (
            Reading.query.with_entities(
                getattr(Reading, measurement), Reading.timestamp
            )
            .filter_by(sensor_id=sensor_id)
            .filter(Reading.timestamp > lower_limit)
            .filter(Reading.timestamp < upper_limit)
        )

        result = readings_schema.dump(readings_for_sensor)

        if not len(result):
            return (
                {"msg": "No readings found for this sensor ID for the given timeframe"},
                404,
            )
        return jsonify(result)

    except TypeError:
        return (
            {
                "msg": "Queries must include a measurement, date upper_limit and date lower_limit"
            },
            400,
        )

    except AttributeError:
        return (
            {
                "msg": "Queries must include a measurement, date upper_limit and date lower_limit"
            },
            400,
        )

    except ValueError:
        return (
            {
                "msg": "upper_limit & lower_limit must be formatted 'YYYY-MM-DD' (time can be suffixed but will be ignored)"
            },
            400,
        )
