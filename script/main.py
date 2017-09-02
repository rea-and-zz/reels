from flask import Flask
from flask import json
from flask import Response
from flask import request
import reelsEngine


app = Flask(__name__)
app.debug = True

engine = reelsEngine.reelsEngine()

@app.route("/reels/query")
def query():
	# get arguments
	user = request.args['user']
	freeText = request.args['freeText']
	genre = request.args['gen']
	fromYear = int(request.args['fromYear'])
	toYear = int(request.args['toYear'])
	pageNum = int(request.args['pageNum'])
	# execute query
	data = engine.query(user, freeText, genre, fromYear, toYear, pageNum)
	# create json response
	js = json.dumps(data)
	resp = Response(js, status=200, mimetype='application/json')
 	resp.headers['Link'] = 'http://reels.com'
	return resp

@app.route("/reels/mymovies")
def query():
	# get arguments
	userId = request.args['userId']
	# execute query
	data = engine.getSuggestion(userId)
	# create json response
	js = json.dumps(data)
	resp = Response(js, status=200, mimetype='application/json')
 	resp.headers['Link'] = 'http://reels.com'
	return resp

@app.route("/reels/info")
def query():
	# get arguments
	movieId = request.args['movieId']
	# execute query
	data = engine.getMovieInfo(movieId)
	# create json response
	js = json.dumps(data)
	resp = Response(js, status=200, mimetype='application/json')
 	resp.headers['Link'] = 'http://reels.com'
	return resp

@app.route("/reels/details")
def query():
	# get arguments
	movieId = request.args['movieId']
	# execute query
	data = engine.getMovieDetails(movieId)
	# create json response
	js = json.dumps(data)
	resp = Response(js, status=200, mimetype='application/json')
 	resp.headers['Link'] = 'http://reels.com'
	return resp

@app.route('/reels/like', methods = ['POST'])
def like():	
	if request.headers['Content-Type'] == 'application/json':
		# execute query
		engine.like(request.json["userId"], request.json["movieId"])
		return "JSON Message: " + json.dumps(request.json)
	else:
		return "415 Unsupported Media Type ;)"

if __name__ == "__main__":
    app.run()

