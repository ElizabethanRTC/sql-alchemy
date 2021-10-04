import sqlalchemy
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from datetime import date


from flask import Flask, jsonify
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.roles import GroupByRole

hawaii_engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(hawaii_engine, reflect= True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(hawaii_engine)

app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes"""
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/startend<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(hawaii_engine)
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    query_d_p = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prior_year).all()
    session.close()
    
    d_p_rows = [{"date": result[0], "prcp": result[1]} for result in query_d_p]  
    d_p_rows
         
    return jsonify (d_p_rows)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(hawaii_engine)
    results = session.query((station.station)).all()
    session.close()
    
    all_stations = list(np.ravel(results)) 
    return jsonify (all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    query_d_t = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= prior_year).\
    filter(measurement.station == 'USC00519281').all()
    session.close()
    d_t_rows = [{"date": result[0], "temperature": result[1]} for result in query_d_t]  

    return jsonify (d_t_rows)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(hawaii_engine)
    sel = [measurement.date,
        func.max(measurement.tobs),
        func.min(measurement.tobs),
        func.avg(measurement.tobs)]
    start = session.query(*sel).\
        filter(measurement.date).\
        group_by(measurement.date).\
        order_by(measurement.date).all()
    session.close()
    start_rows = [{"date": result[0], "max": result[1], "min": result[2], "avg": result[3] } for result in start]
    return jsonify(start_rows)  
   
@app.route("/api/v1.0/<startend>")
def startend(start, end):
    start_date = dt.datetime(2010, 1, 1)
    end_date = dt.datetime(2017, 8, 23)
    session = Session(hawaii_engine) 
    sel = [measurement.date,
        func.max(measurement.tobs),
        func.min(measurement.tobs),
        func.avg(measurement.tobs)]
    start_end = session.query(*sel).\
        filter(measurement.date >= start_date).\
        filter(measurement.date >= end_date).\
        group_by(measurement.date).\
        order_by(measurement.date).all().\
        session.close()
    start_end_rows = [{"date": result[0], "max": result[1], "min": result[2], "avg": result[3] } for result in startend]
    return jsonify(start_end_rows)
 
if __name__ == "__main__":
    app.run(debug=True)
    