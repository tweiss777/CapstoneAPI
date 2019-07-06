import flask
from flask import request,jsonify

# Create the app
app = flask.Flask(__name__)

# Enable debugging
app.config["DEBUG"] = True


# Hard-coded array
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

#basic way of mapping a url to a function
@app.route('/',methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


# This function outputs the json data for all books
@app.route('/api/v1/resources/books/all',methods=['GET'])
def api_all():
    return jsonify(books)


# This function outputs json data for books with a corresponding is
@app.route('/api/v1/resources/books/',methods=['GET'])
def api_id():
    # Check if the id param is in the url
    # This would be the case if the user passes an int
    # If so, assign to int.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No ID was passed into the parameter"

    # holds our json data
    results = []

    # iterate through our books list
    # check if the id in the url matches the value of the id key.
    # if so, append the book to the results
    for book in books:
        if book['id'] == id:
            results.append(book)
    
    if len(results) < 1:
        return "Error: No data :("

    return jsonify(results)

"""request.json is used when handling post requests
whereas request.args is ued when handling get requests"""
@app.route('/api/v1/resources/post',methods=['POST'])
def api_id_post():
    print("recieved request")
    if request.method == 'POST':
        if 'id' in request.json:
            id = int(request.json['id'])
        else:
            return "Error: no id was passed in the request"

        results = []
        for book in books:
            if book['id'] == id:
                results.append(book)
        if len(results) < 1:
            return "Error: No data :("

        return jsonify(results)
    return "Error on request"

# This line below runs the app
app.run()