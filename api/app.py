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
    user_id = db.Column(db.String(40))
    first_name = db.Column(db.String(40))
    surname = db.Column(db.String(40))
    email = db.Column(db.String(60), unique=True)
    sensor_id = db.Column(db.String(20), unique=True, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    readings = db.relationship("Reading", backref="user", lazy="select")

    def __init__(self, user_id, first_name, surname, email, sensor_id, username):
        self.user_id = user_id
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.sensor_id = sensor_id
        self.username = username


# Reading Class / Model
class Reading(db.Model):
    reading_id = db.Column(db.Integer, primary_key=True)
    temp_mean = db.Column(db.Integer)
    pressure_mean = db.Column(db.Integer)
    humidity_mean = db.Column(db.Integer)
    total_quality_mean = db.Column(db.Integer)
    sensor_id = db.Column(db.String(20), db.ForeignKey("user.sensor_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(
        self, temp_mean, pressure_mean, humidity_mean, total_quality_mean, sensor_id
    ):
        self.temp_mean = temp_mean
        self.pressure_mean = pressure_mean
        self.humidity_mean = humidity_mean
        self.total_quality_mean = total_quality_mean
        self.sensor_id = sensor_id


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
            "total_quality_mean",
            "sensor_id",
            "timestamp",
        )


# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
reading_schema = ReadingSchema()
readings_schema = ReadingSchema(many=True)


# Routes
@app.route("/user", methods=["POST"])
def post_user():
    import controller

    return controller.insert_user(request)


@app.route("/user", methods=["GET"])
def get_all_users():
    import controller

    return controller.select_all_users()


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
