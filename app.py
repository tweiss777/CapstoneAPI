import flask
import redis
from flask import jsonify, request
from rq import Queue
from rq.job import Job
from rq.registry import FinishedJobRegistry, StartedJobRegistry
from worker import conn
from JobUtils.Driver import main as retrieveApiData

# Create the app
app = flask.Flask(__name__)

# Enable debugging
app.config["DEBUG"] = True

# initialize the redis worker connection
redisConnection = conn

# initialize the queue
queue = Queue(connection=redisConnection)


# started and finished jobs registries (both will listen on the default worker)
startRegister = StartedJobRegistry('default',connection=redisConnection)
finishRegister = FinishedJobRegistry('default',connection=redisConnection)
"""This is action that will be called when running the api
    Returns json data"""
    # IMPLEMENTATION INCOMPLETE
    # THIS IS WHAT IS GOING TO BE CALLED IN MY TEST SCRIPT
@app.route('/api/v1/bestjobs',methods=['POST'])
def getJobData():
    correctKey = "SSTFZ05I7GYVFVTV9Y4S7DCQOUQ0Y1VHNM6AOS2XHRUUCVG8A7JE15FH8KR3SFWVQ1HH92VD91LE7D7U8U2YTAFL5VAQBM6CMU7V"
    # Add request headers
    rheaders = request.headers
    
    # api key check
    authentication = rheaders.get("X-Api-Key")
    if authentication == correctKey:
        # Parameters to pass to function
        query = request.json['query']
        zipcode = request.json['zipcode']
        resumeStr = request.json['resume']
        
        # response from the capstone algorithm
        # results = retrieveApiData(query,zipcode,resumeStr)
        
        # store process to be run by the queue
        process = queue.enqueue(retrieveApiData,args=(query,zipcode,resumeStr))
        
        # return the process id
        return jsonify({"message": "processing the job this may take some time...",
                        "process_id": process.id}),200
    return jsonify({"Message":"Access denied,"}),401


# function that pings the server for the response
# this should be called by the client
@app.route("/api/v1/checkresults",methods=["GET"])
def returnResults():
    # retrieve the process id from the url
    process_id = request.args.get('pid')
    # if pid is empty or invlaid
    if process_id is None:
        return jsonify({"message":"invalid params"}),400

    elif process_id not in startRegister.get_job_ids() and process_id not in finishRegister.get_job_ids():
        return jsonify({"message": "invalid pid"}), 400

    # fetch the job handled by redis queue
    currentJob = Job.fetch(process_id,redisConnection)
    
    # return a status 202 if the job is still processing 
    if currentJob.result is None:
        return jsonify({"message":"job is still processing...."}),202

    # return a 200 status along with the results
    return jsonify(currentJob.result),200

# This line below runs the app
if __name__ == "__main__":
    app.run()
