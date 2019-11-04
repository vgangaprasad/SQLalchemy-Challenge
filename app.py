from  flask import Flask, jsonify
import time
from datetime import datetime
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# Set up query engine. 'echo=True is the default - will keep a log of activities'
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

# Create our Flask app

app = Flask(__name__)




@app.route("/")
def home():
    print("Request received for Home page")
    return(f"Welcome to Climate Analysis Home page! </br>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation </br>"
            f"/api/v1.0/stations </br>"
            f"/api/v1.0/tobs </br>"
            f"/api/v1.0/<start> </br>"
            f"/api/v1.0/<start>/<end> </br>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()


    precipitation_results = {}

    for result in results:
    
        precipitation_results[result.date] = result.prcp

    return jsonify(precipitation_results)




@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Return a JSON list of stations from the dataset.
    results = session.query(Measurement.station).group_by(Measurement.station).order_by(Measurement.station).all()
    all_stations = []

    for stat in results:
        all_stations.append(stat)
    
    return jsonify(all_stations)




@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    print(last_data_point)
    x=datetime.strptime(last_data_point, '%Y-%m-%d')
    x -= timedelta(days=365)
    date_1_year_prior = x.strftime('%Y-%m-%d')
    print(date_1_year_prior)

    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= date_1_year_prior).all()
    tobs_results = []

    for tob in results:
        tobs_dict = {}
        tobs_dict['date'] = tob.date
        tobs_dict['station'] = tob.station
        tobs_dict['tobs'] = tob.tobs

        tobs_results.append(tobs_dict)
    
    return jsonify(tobs_results)




@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

def calc_temps(start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    Argumentss:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        Date, Min, Average and TMAX
    """
    
    session = Session(engine)
    
    sel = [Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end_date == None:
        result = session.query(*sel).\
            group_by(Measurement.date).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= start_date).all()

    else:
        result = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            filter(Measurement.date <= end_date).all()

    result_list = []
    
    for x in result:
    
        result_dict = {
            "date" : x[0],
            "TMIN" : x[1],
            "TAVG" : x[2],
            "TMAX" : x[3]
        }
        result_list.append(result_dict)
    
    return jsonify(result_list)


if __name__ == "__main__":
    app.run(debug=True)