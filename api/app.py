from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

# Initialise the app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database initialisation
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Users Class / Model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40))
    surname = db.Column(db.String(40))
    email = db.Column(db.String(60), unique=True)
    sensor_id = db.Column(db.String(20), unique=True)
    username = db.Column(db.String(40), unique=True)

    def __init__(self, first_name, surname, email, sensor_id, username):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.sensor_id = sensor_id
        self.username = username


# Reading Class / Model


class Reading(db.Model):
    reading_id = db.Column(db.Integer, primary_key=True)
    temp_mean = db.Column(db.Float)
    pressure_mean = db.Column(db.Float)
    humidity_mean = db.Column(db.Float)
    tvoc_mean = db.Column(db.Float)
    sensor_id = db.Column(db.String(20), db.ForeignKey("user.sensor_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    baseline_temp = db.Column(db.Float)
    gas_baseline = db.Column(db.Float)

    def __init__(
        self,
        temp_mean,
        pressure_mean,
        humidity_mean,
        tvoc_mean,
        sensor_id,
        baseline_temp,
        gas_baseline,
    ):
        self.temp_mean = temp_mean
        self.pressure_mean = pressure_mean
        self.humidity_mean = humidity_mean
        self.tvoc_mean = tvoc_mean
        self.sensor_id = sensor_id
        self.baseline_temp = baseline_temp
        self.gas_baseline = gas_baseline


# User Schema (using marshmallow)
class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "first_name", "surname", "email", "sensor_id", "username")


# Reading Schema
class ReadingSchema(ma.Schema):
    class Meta:
        fields = (
            "reading_id",
            "temp_mean",
            "pressure_mean",
            "humidity_mean",
            "tvoc_mean",
            "sensor_id",
            "timestamp",
            "baseline_temp",
            "gas_baseline",
        )


# Init Schema
user_schema = UserSchema()  # May need to add strict=True to both invokations
# users_schema = UserSchema(many=True)
reading_schema = ReadingSchema()
readings_schema = ReadingSchema(many=True)


@app.route("/user", methods=["POST"])
def post_user():
    first_name = request.json["first_name"]
    surname = request.json["surname"]
    email = request.json["email"]
    sensor_id = request.json["sensor_id"]
    username = request.json["username"]

    new_user = User(first_name, surname, email, sensor_id, username)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


@app.route("/user/<username>", methods=["GET"])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    return user_schema.jsonify(user)


@app.route("/reading/<sensor_id>", methods=["POST"])
def post_reading(sensor_id):
    sensor_id = sensor_id
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


@app.route("/reading/<sensor_id>", methods=["GET"])
def get_readings(sensor_id):
    all_readings_for_sensor = Reading.query.filter_by(sensor_id=sensor_id).limit(8640)
    result = readings_schema.dump(all_readings_for_sensor)
    return jsonify(result)


@app.route("/most_recent_reading/<sensor_id>", methods=["GET"])
def get_most_recent_reading(sensor_id):
    most_recent_reading = (
        Reading.query.filter_by(sensor_id=sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    print(most_recent_reading)
    return reading_schema.jsonify(most_recent_reading)


# Run server
if __name__ == "__main__":
    app.run(debug=True)
