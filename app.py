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
@app.route('/api/v1/bestjobs',methods=['POST'])
def getJobData():
    correctKey = "SSTFZ05I7GYVFVTV9Y4S7DCQOUQ0Y1VHNM6AOS2XHRUUCVG8A7JE15FH8KR3SFWVQ1HH92VD91LE7D7U8U2YTAFL5VAQBM6CMU7V"
    # Add request headers
    rheaders = request.headers
    
    authentication = rheaders.get("X-Api-Key")
    if authentication == correctKey:
        # Parameters to pass to function
        query = request.json['query']
        zipcode = request.json['zipcode']
        resumeStr = request.json['resume']
        
        # response from the capstone algorithm
        results = retrieveApiData(query,zipcode,resumeStr)
        return jsonify(results),200
    else:
        return jsonify({"Message":"Access denied,"}),401

# This line below runs the app
if __name__ == "__main__":
    app.run()
