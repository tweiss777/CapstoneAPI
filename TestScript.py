import json,requests, sys
#TEST SCRIPT

if __name__ == "__main__":

    jobSearch = sys.argv[1]
    zipCode = sys.argv[2]
    resumeAsDocFile = sys.arv[3]


    # API endpoint
    endpoint = "http://127.0.0.1:5000/api/v1/resources/post"

    # data to pass to the server
    data = {'id': 1}

    # Request
    r = requests.post(url=endpoint ,json=data)

    # Response
    print(r.status_code,r.reason,r.text)

