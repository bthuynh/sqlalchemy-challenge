import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine,reflect = True)

#Used to find classes
#print(Base.classes.keys())
#['measurement', 'station']

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    prcp_list = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(Station.name).all()
    session.close()
    
    all_stations = list(np.ravel(station_results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    date_query = dt.date(2017,8,23) - dt.timedelta(days=365)
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= date_query).order_by(Measurement.date).all()
    session.close()
    
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = dt.date(2010,1,1)
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close

    start_list = []
    for min, avg, max in start_results:
        start_dict = {}
        start_dict["StartDate"] = start_date
        start_dict["Min"] = min
        start_dict["Avg"] = avg
        start_dict["Max"] = max
        start_list.append(start_dict)
    
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    
    start_date = dt.date(2010,1,1)
    end_date = dt.date(2017,8,23)
    
    startend_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        group_by(Measurement.date).all()
        
    session.close()
    
    startend_list = []
    for min, avg, max in startend_results:
        startend_dict = {}
        startend_dict["StartDate"] = start_date
        startend_dict["EndDate"] = end_date
        startend_dict["Min"] = min
        startend_dict["Avg"] = avg
        startend_dict["Max"] = max
        startend_list.append(startend_dict)

    return jsonify(startend_list)


if __name__ == "__main__":
    app.run(debug=True)