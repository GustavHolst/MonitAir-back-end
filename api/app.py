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
reading_schema = ReadingSchema()
readings_schema = ReadingSchema(many=True)


@app.route("/user", methods=["POST"])
def post_user():
    import controller

    return controller.insert_user(request)


@app.route("/user/<username>", methods=["GET"])
def get_user(username):
    import controller

    return controller.select_user(username)


@app.route("/reading/<sensor_id>", methods=["POST"])
def post_reading(sensor_id):
    import controller

    return controller.insert_reading(sensor_id)


@app.route("/reading/<sensor_id>", methods=["GET"])
def get_readings(sensor_id):
    import controller

    return controller.select_readings(sensor_id)


@app.route("/most_recent_reading/<sensor_id>", methods=["GET"])
def get_most_recent_reading(sensor_id):
    import controller

    return controller.select_most_recent_reading(sensor_id)


# Run server
if __name__ == "__main__":
    app.run(debug=True)
