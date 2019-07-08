import flask
from flask import request,jsonify
from JobUtils.Driver import main as retrieveApiData

# Create the app
app = flask.Flask(__name__)

# Enable debugging
app.config["DEBUG"] = True

"""This is action that will be called when running the api
    Returns json data"""
    # IMPLEMENTATION INCOMPLETE
    # THIS IS WHAT IS GOING TO BE CALLED IN MY TEST SCRIPT
@app.route('/api/v1/getJsonData',methods=['POST'])
def getJobData():
    # Print statement used for debugging purposes
    print("request recieved")
    
    # Parameters to pass to function
    query = request.json['query']
    zipcode = request.json['zipcode']
    resumeStr = request.json['resume']
    
    # response from the capstone algorithm
    results = retrieveApiData(query,zipcode,resumeStr)
    return jsonify(results)

# This line below runs the app
app.run()