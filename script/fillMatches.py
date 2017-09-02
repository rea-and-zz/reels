#!/usr/bin/python
# coding: utf_8

import MySQLdb
import sys
import reelsEngine
import random

# connect to the movie app DB
conn = MySQLdb.connect( host="127.0.0.1", port=3306,
                  user="root",
                  passwd="andrea79",
                  db="MovieApp")
                 
# get cursor 
x = conn.cursor()
y = conn.cursor()
itemNum = 0

# first fill the movie metches
x.execute("""SELECT * FROM `MovieApp`.`Movie`""")
for outerRow in x:
	# process each movie, one by one
	idMovie = outerRow[0]
	print "Processing movie " + str(idMovie)
	thisMovieMatches = {}
	y.execute("""SELECT * FROM `MovieApp`.`User_liked_MoviesCSV`""")
	for innerRow in y:
		#print "Looking for matches in user " + str(innerRow[0])
		moviesCsv = innerRow[1]
		moviesList = moviesCsv.split(',')
		if str(idMovie) in moviesList:
			# this user liked the movie, let's consider the other ones as candidates...
			#print "Movie found !"
			moviesList.remove(str(idMovie))
			for relatedMovie in moviesList:
				if relatedMovie not in thisMovieMatches:
					thisMovieMatches[relatedMovie] = 1
				else:
					thisMovieMatches[relatedMovie] = thisMovieMatches[relatedMovie] + 1

	metchesCsv = ""
	#print "Sorting this movie matched dictionary..."
	for key, value in sorted(thisMovieMatches.iteritems(), key=lambda (k,v): (v,k), reverse = True)[0:100]:
		#print "%s: %s" % (key, value)
		if len(metchesCsv) == 0:
			metchesCsv = key
		else:
			metchesCsv = metchesCsv + "," + key

	y.execute("""DELETE FROM `MovieApp`.`Movie_MatchingMovies` where idMovie = (%s)""", (idMovie))
	y.execute("""INSERT INTO `MovieApp`.`Movie_MatchingMovies` (`idMovie`, `matchingMovies`) VALUES (%s, %s)""", (idMovie, metchesCsv))
	conn.commit()

print "Done!"
conn.commit()
conn.close()