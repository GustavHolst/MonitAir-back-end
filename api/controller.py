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

    except:
        return {"msg": "something else"}


def select_user(username):
    user = User.query.filter_by(username=username).first()

    if isinstance(user, User):
        return user_schema.jsonify(user)

    return {"msg": "user not found"}, 404


def select_all_users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)


def insert_reading(sensor_id):
    db.session.rollback()
    try:
        temp_mean = round(request.json["temp_mean"])
        pressure_mean = round(request.json["pressure_mean"])
        humidity_mean = round(request.json["humidity_mean"])
        total_quality_mean = round(100 - request.json["total_quality_mean"] * 5)
        new_reading = Reading(
            temp_mean, pressure_mean, humidity_mean, total_quality_mean, sensor_id
        )
        db.session.add(new_reading)
        db.session.commit()

        return reading_schema.jsonify(new_reading), 201

    except KeyError:
        return {"msg": "Info missing from post reading request"}, 400


def select_readings(sensor_id):
    try:
        measurement = request.args.get("measurement")
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
                {"msg": "no readings found for this sensor ID for the given timeframe"},
                404,
            )
        return jsonify(result)

    except TypeError:
        return (
            {
                "msg": "Bad Request: queries must include a measurement, date upper_limit and date lower_limit"
            },
            400,
        )

    except AttributeError:
        return (
            {
                "msg": "Bad Request: queries must include a measurement, date upper_limit and date lower_limit"
            },
            400,
        )


def select_most_recent_reading(sensor_id):
    most_recent_reading = (
        Reading.query.filter_by(sensor_id=sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    if not most_recent_reading:
        return (
            {"msg": "no readings found for this sensor ID"},
            404,
        )
    return reading_schema.jsonify(most_recent_reading)
