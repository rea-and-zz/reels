#!/usr/bin/python

import MySQLdb
import sys


upTo = -1
if len(sys.argv) > 1:
	upTo = int(sys.argv[1])
	print upTo

# connect to the movie app DB
conn = MySQLdb.connect( host="127.0.0.1", port=3306,
                  user="root",
                  passwd="andrea79",
                  db="MovieApp")
                 
# get cursor 
x = conn.cursor()

dbfile = open('../archives/omdb.txt','r')
itemNum = 0

genresDict = dict()
celebDict = dict()

directorDictForCSV = dict()
actorDictForCSV = dict()

for line in dbfile: 
	
	# skip first line...
	itemNum = itemNum + 1
	if itemNum == 1:
		#skip firs line...
		continue

	if upTo != -1 and itemNum >= upTo:
		break
	
	values = line.split('\t', 30)
	rowId = values[0]
	imdbId = values[1]
	title = values[2]
	year = values[3]
	rating = values[4]
	runtime = values[5]	
	genre =	values[6]	 
	released = values[7]	
	director = values[8]	
	writer = values[9]	
	cast = values[10]		
	imdbRating = values[11]	
	imdbVotes = values[12]	
	posterUrl = values[13]	
	plot = values[14]		
	fullPlot = values[15]		
	lastUpdated = values[16]

	# rating sanity check and normaization
	if imdbRating == "N/A" or imdbRating == "Not Rated":
		imdbRating = -1
	else:
		imdbRating = imdbRating * 10

	# more  sanity check
	if plot == "N/A":
		plot = "-"
	if fullPlot == "N/A":
		fullPlot = "-"
	if posterUrl == "N/A":
		posterUrl = "-"

	# add to movies table
	#print "Adding movie: " +  title + " " + imdbId + " " + year
	autoMovieId = -1
	try:
		x.execute("""INSERT INTO `MovieApp`.`Movie` (`title`, `plot`, `year`, `thumbUrl`, `rating`, `fullPlot`, `imdbId`)  VALUES (%s, %s, %s, %s, %s, %s, %s)""", (title, plot, year, posterUrl, imdbRating, fullPlot, imdbId))
   		x.execute('SELECT LAST_INSERT_ID() AS id')
   		autoMovieId = x.fetchone()[0]

	except MySQLdb.ProgrammingError as error:
        	print "---->SQL Error: %s" % error
        	conn.rollback()

	except MySQLdb.IntegrityError as e:
        	print "--->SQL Error: %s" % e    
        	conn.rollback()

	# update genre table
	if genre != "N/A":
		genreList = genre.split(', ', 30)
		genresCSV = ""
		#print genreList

		try:
			for genreName in genreList:
				autoGenId = -1
				# first make sure this one is already in the db

				#x.execute("""SELECT * FROM `MovieApp`.`Genre` WHERE name LIKE (%s)""",  (genreName))
				#numrows = int (x.rowcount)
				#if numrows<1:
				if genreName not in genresDict:
					x.execute("""INSERT INTO `MovieApp`.`Genre` (`name`) VALUES (%s)""", (genreName))
					x.execute('SELECT LAST_INSERT_ID() AS id')
					genresDict[genreName] = x.fetchone()[0];
   				
   				# in any case, get the genre id	
   				autoGenId = genresDict[genreName]

   				# then let's link it to this movie
   				if autoGenId >= 0:
					x.execute("""INSERT INTO `MovieApp`.`Movie_Genre` (`idMovie`, `idGenre`, `rating`) VALUES (%s, %s, %s)""", (autoMovieId, autoGenId, imdbRating))

				# Redundancy: update the Movie -> Directors (CSV) table too
				if genresCSV == "":
					genresCSV = str(autoGenId)
				else:
					genresCSV = genresCSV + "," + str(autoGenId)

			# All genres for this movie parsed
			x.execute("""INSERT INTO `MovieApp`.`Movie_GenresCSV` (`idMovie`, `genres`) VALUES (%s, %s)""", (autoMovieId, genresCSV))

		except MySQLdb.ProgrammingError as error:
			print "---->SQL Error: %s" % error
			conn.rollback()

	# update celebrities table for director
	if director != "N/A":
		directorList = director.split(', ', 30)
		directorsCSV = ""
		#print directorList
		
		try:
			for directorName in directorList:
				if directorName == "N/A":
					continue
				
				autoGenCeleb = -1
				# first make sure this one is already in the db

				#x.execute("""SELECT * FROM `MovieApp`.`Celebrity` WHERE name LIKE (%s)""",  (directorName))
				#numrows = int (x.rowcount)
				#if numrows<1:
				if directorName not in celebDict:
					x.execute("""INSERT INTO `MovieApp`.`Celebrity` (`name`) VALUES (%s)""", (directorName))
					x.execute('SELECT LAST_INSERT_ID() AS id')
					celebDict[directorName] = x.fetchone()[0];
	   			
	   			# in any case, get the celeb id	
	   			autoGenCeleb = celebDict[directorName]

	   			# then let's link him/her to this movie
	   			if autoGenCeleb >= 0:
					x.execute("""INSERT INTO `MovieApp`.`Movie_Director` (`idMovie`, `idDirector`) VALUES (%s, %s)""", (autoMovieId, autoGenCeleb))

				# Redundancy: update the Director -> Movies (CSV) table too
				if autoGenCeleb not in directorDictForCSV:
					x.execute("""INSERT INTO `MovieApp`.`Director_MoviesCSV` (`idDirector`, `movies`) VALUES (%s, %s)""", (autoGenCeleb, str(autoMovieId)))
					directorDictForCSV[autoGenCeleb] = str(autoMovieId)
				else:
					newCSV = directorDictForCSV[autoGenCeleb] + "," + str(autoMovieId)
					x.execute("UPDATE `MovieApp`.`Director_MoviesCSV` SET movies=%s  WHERE idDirector = (%s)""",  (newCSV, autoGenCeleb))
					directorDictForCSV[autoGenCeleb] = newCSV

				# Redundancy: update the Movie -> Directors (CSV) table too
				if directorsCSV == "":
					directorsCSV = str(autoGenCeleb)
				else:
					directorsCSV = directorsCSV + "," + str(autoGenCeleb)
				
			# All directiors for this movie parsed
			x.execute("""INSERT INTO `MovieApp`.`Movie_DirectorsCSV` (`idMovie`, `directors`) VALUES (%s, %s)""", (autoMovieId, directorsCSV))
		
		except MySQLdb.ProgrammingError as error:
			print "---->SQL Error: %s" % error
			conn.rollback()

	# update celebrities table for cast
	if cast != "N/A":
		castList = cast.split(', ', 30)
		actorsCSV = ""
		#print castList

		try:
			for castName in castList:
				autoGenCeleb = -1
				# first make sure this one is already in the db

				#x.execute("""SELECT * FROM `MovieApp`.`Celebrity` WHERE name LIKE (%s)""",  (castName))
				#numrows = int (x.rowcount)
				#if numrows<1:
				if castName not in celebDict:
					x.execute("""INSERT INTO `MovieApp`.`Celebrity` (`name`) VALUES (%s)""", (castName))
					x.execute('SELECT LAST_INSERT_ID() AS id')
					celebDict[castName] = x.fetchone()[0];
   			
   				# in any case, get the celeb id	
   				autoGenCeleb = celebDict[castName]

   				# then let's link him/her to this movie
   				if autoGenCeleb >= 0:
					x.execute("""INSERT INTO `MovieApp`.`Movie_Actor` (`idMovie`, `idActor`) VALUES (%s, %s)""", (autoMovieId, autoGenCeleb))

				# Redundancy: update the Director -> Movies (CSV) table too
				if autoGenCeleb not in actorDictForCSV:
					x.execute("""INSERT INTO `MovieApp`.`Actor_MoviesCSV` (`idActor`, `movies`) VALUES (%s, %s)""", (autoGenCeleb, str(autoMovieId)))
					actorDictForCSV[autoGenCeleb] = str(autoMovieId)
				else:
					newCSV = actorDictForCSV[autoGenCeleb] + "," + str(autoMovieId)
					x.execute("UPDATE `MovieApp`.`Actor_MoviesCSV` SET movies=%s  WHERE idActor = (%s)""",  (newCSV, autoGenCeleb))
					actorDictForCSV[autoGenCeleb] = newCSV
				
				# Redundancy: update the Movie -> Directors (CSV) table too
				if actorsCSV == "":
					actorsCSV = str(autoGenCeleb)
				else:
					actorsCSV = actorsCSV + "," + str(autoGenCeleb)

			# All actors for this movie parsed
			x.execute("""INSERT INTO `MovieApp`.`Movie_ActorsCSV` (`idMovie`, `actors`) VALUES (%s, %s)""", (autoMovieId, actorsCSV))

		except MySQLdb.ProgrammingError as error:
			print "---->SQL Error: %s" % error
			conn.rollback()
	
	if itemNum % 100 == 0:
    		print "Saved so far: " + str(itemNum)
    		conn.commit()
	
print "Done! Movies parsed: " + str(itemNum)
conn.commit()
dbfile.close()
conn.close()

