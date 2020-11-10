import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify



# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
S = Base.classes.station
M = Base.classes.measurement


# Flask Setup
#################################################
app = Flask(__name__)


# Flask Routes
#################################################

@app.route("/")
@app.route("/home")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/start_date/<start>/end_date/<end>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all date and precipitation data"""
    # Query all date and precipitation data
    results = session.query(M.date, M.prcp).all()

    session.close()

    #  Create a dictionary from the row data and append to a list
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all date and precipitation data
    results = session.query(S.name).group_by(S.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the last date and calculate the date 1 year ago
    last_date = session.query(func.max(M.date)).first()
    last_date = datetime.strptime(last_date[0], "%Y-%m-%d")
    query_date = last_date - dt.timedelta(days=365)
    
    # Query most active station
    station_list = session.query(M.station, S.name, func.count(M.station)) \
                      .filter(M.station == S.station) \
                      .filter(M.date >= query_date) \
                      .group_by(M.station) \
                      .order_by(func.count(M.station).desc()).first()
    active_station = station_list[0]

    """Return a dictionary of date and tobs data"""
    # Query all date and temperature observations data
    results = session.query(M.date, M.tobs) \
                     .filter(M.station == active_station)\
                     .filter(M.date >= query_date) \
                     .order_by(M.date.desc()).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    active_tobs_last_year = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        active_tobs_last_year.append(tobs_dict)

    return jsonify(active_tobs_last_year)



@app.route("/api/v1.0/start_date/<start_date>")
def date_from(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of temperature summary"""
    # Query all temperature summary from specified start date
    date_from = session.query(func.min(M.tobs),func.avg(M.tobs),func.max(M.tobs))\
                  .filter(M.date >= start_date).all()

    session.close()

    tmin = date_from[0][0]
    tavg = date_from[0][1]
    tmax = date_from[0][2]
    
    #  Create a dictionary from the row data
    temp_summary = {}
    temp_summary["TMIN"] = tmin
    temp_summary["TAVG"] = round(tavg,2)
    temp_summary["TMAX"] = tmax
    print (date_from[0])    
    return jsonify(temp_summary)


@app.route("/api/v1.0/start_date/<start_date>/end_date/<end_date>")
def start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of temperature summary"""
    # Query all temperature summary from specified start date
    date_from = session.query(func.min(M.tobs),func.avg(M.tobs),func.max(M.tobs))\
                       .filter(M.date >= start_date) \
                       .filter(M.date <= end_date).all()

    session.close()
    
    tmin = date_from[0][0]
    tavg = date_from[0][1]
    tmax = date_from[0][2]

    #  Create a dictionary from the row data
    temp_summary = {}
    temp_summary["TMIN"] = tmin
    temp_summary["TAVG"] = round(tavg,2)
    temp_summary["TMAX"] = tmax

    return jsonify(temp_summary)


if __name__ == '__main__':
    app.run(debug=True)
