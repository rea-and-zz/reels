import MySQLdb
import sys
import operator

class reelsEngine(object):

	def __init__(self):
		# connect to the movie app DB
		self.conn = MySQLdb.connect( host="127.0.0.1", port=3306,
                  user="root",
                  passwd="andrea79",
                  db="MovieApp")    

		# get cursor 
		self.x = self.conn.cursor()
		self.y = self.conn.cursor()

		# set varchar encoding
		self.x.execute('SET NAMES utf8;')
		self.x.execute('SET CHARACTER SET utf8;')
		self.x.execute('SET character_set_connection=utf8;')

		#set page size
		self.pageSize = 10


	def engineName(self):
		return "Thie is The Reels app engine"

	def getSeenIds(self, user):
		movies = []
		self.x.execute("""SELECT * FROM `MovieApp`.`User_seen_MoviesCSV` WHERE idUser = (%s)""", (user))
		if int(self.x.rowcount) > 0:
			csv = self.x.fetchone()[1]
			movies = csv.split(',')
   	 	return movies

	def getQueuedIds(self, user):
		movies = []
		self.x.execute("""SELECT * FROM `MovieApp`.`User_queued_MoviesCSV` WHERE idUser = (%s)""", (user))
		if int(self.x.rowcount) > 0:
			csv = self.x.fetchone()[1]
			movies = csv.split(',')
   	 	return movies

  	def getHidesIds(self, user):
   	 	movies = []
		self.x.execute("""SELECT * FROM `MovieApp`.`User_hide_MoviesCSV` WHERE idUser = (%s)""", (user))
		if int(self.x.rowcount) > 0:
			csv = self.x.fetchone()[1]
			movies = csv.split(',')
   	 	return movies			

   	def getMovieInfo(self, idMovie):
		resp = dict()
		self.x.execute("""SELECT * FROM `MovieApp`.`Movie` inner join `MovieApp`.`Movie_GenresCSV` ON Movie.idMovie = Movie_GenresCSV.idMovie inner join `MovieApp`.`Movie_DirectorsCSV` ON Movie.idMovie = Movie_DirectorsCSV.idMovie inner join `MovieApp`.`Movie_ActorsCSV` ON Movie.idMovie = Movie_ActorsCSV.idMovie WHERE Movie.idMovie = (%s)""",  (idMovie))
		if int(self.x.rowcount) > 0:
			row = self.x.fetchone()
			#print row
			resp["id"] = row[0]
			resp["title"] = row[1]
			resp["year"] = row[3]
			resp["rating"] = row[4]
			resp["thumb"] = row[6]
			resp["gens"] = row[9]
			resp["dirs"] = ""
			resp["actors"] = ""
			# add director names
			directorsCsv = str(row[11])
			directorsIds = directorsCsv.split(',')
			for directorId in directorsIds:
				self.x.execute("""SELECT * FROM `MovieApp`.`Celebrity` WHERE idCelebrity = (%s)""",  (directorId))
				if int(self.x.rowcount) > 0:
					if len(resp["dirs"]) == 0:
						resp["dirs"] = self.x.fetchone()[1]
					else:
						resp["dirs"] = resp["dirs"] + ',' + self.x.fetchone()[1]
			# add actors names
			actorsCsv = str(row[13])
			actorsIds = actorsCsv.split(',')
			for actorId in actorsIds:
				self.x.execute("""SELECT * FROM `MovieApp`.`Celebrity` WHERE idCelebrity = (%s)""",  (actorId))
				if int(self.x.rowcount) > 0:
					if len(resp["actors"]) == 0:
						resp["actors"] = self.x.fetchone()[1]
					else:
						resp["actors"] = resp["actors"] + ',' + self.x.fetchone()[1]
			#print resp
		return resp

	def getMovieDetails(self, idMovie):
		resp = dict()
		self.x.execute("""SELECT * FROM `MovieApp`.`Movie` WHERE Movie.idMovie = (%s)""",  (idMovie))
		if int(self.x.rowcount) > 0:
			row = self.x.fetchone()
			resp["id"] = row[0]
			resp["plot"] = row[7]
		return resp

	def getSuggestion(self, user):
		# load 'queued' and 'seen' lists, so we don't include them here
		skipList = self.getQueuedIds(user) + self.getSeenIds(user) + self.getHidesIds(user)
		# Ks
		kMaxSuggestedMovies = 2000
		done = False
		listMovies = []
		# SECTION 1
		# 
		# at the very top let's put some "fresh movies" with high ratings
		# should consider user preference in term of genre, if available
		kTopMoviesRatingTreshold = 750
		kTopMoviesMaxSize = 10
		self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_GenresCSV` WHERE idUser = (%s)""",  (user))
		if int(self.x.rowcount) > 0:
			csv = self.x.fetchone()[1]
			genres = csv.split(',')
			#print str(genres)
			for genre in genres:
				self.y.execute("""SELECT * FROM `MovieApp`.`Movie` inner join `MovieApp`.`Movie_Genre` ON Movie.idMovie = Movie_Genre.idMovie where Movie_Genre.idGenre = (%s) and Movie.rating > (%s) order by Movie.idMovie DESC limit %s""", (genre, kTopMoviesRatingTreshold, kTopMoviesMaxSize))
				for row in self.y:
					movieId = row[0]
					if movieId not in listMovies and movieId not in skipList: 
						listMovies.append(movieId)
		# SECTION 2
		#
		# then we consider user's liked movies, and proposed most recurrent "also-liked" for each of them
		if done == False:
			matches = {}
			self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_MoviesCSV` WHERE idUser = (%s)""",  (user))
			for row in self.x:
				csv = row[1]
				movies = csv.split(',')
				for movie in movies:
					self.y.execute("""SELECT * FROM `MovieApp`.`Movie_MatchingMovies` WHERE idMovie = (%s)""",  (str(movie)))
					if int(self.y.rowcount)>0:
						csv = self.y.fetchone()[1]
						matches[movie] = csv.split(',')
			while len(matches) > 0 and done == False: 
				toDelete = []
				for idMovie in matches:
					item = matches[idMovie][0]
					if item not in listMovies and item not in skipList:
						listMovies.append(item)
						if len(listMovies) > kMaxSuggestedMovies:
							done = True
							break
					matches[idMovie].remove(item)
					if len(matches[idMovie]) == 0:
						toDelete.append(idMovie)
				for item in toDelete:
					del matches[item]
		# SECTION 3
		#
		# we continue by looking at the user's liked director, and proposing their other works
		if done == False:
			self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_DirectorsCSV` WHERE idUser = (%s)""", (user))
			if int(self.x.rowcount) > 0:
				csv = self.x.fetchone()[1]
				directorsList = csv.split(',')
				for director in directorsList:
					if done == True:
						break
					self.y.execute("""SELECT * FROM `MovieApp`.`Director_MoviesCSV` WHERE idDirector = (%s)""",  director)
					if int(self.y.rowcount) > 0:
						csv = self.y.fetchone()[1]
						moviesList = csv.split(',')
						for movie in moviesList:
							if movie not in listMovies and movie not in skipList:
								listMovies.append(movie)
								if len(listMovies) > kMaxSuggestedMovies:
									done = True
									break
		# SECTION 4
		#
		# we continue by looking at the user's liked actors, and proposing their other works
		if done == False:
			self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_ActorsCSV` WHERE idUser = (%s)""", (user))
			if int(self.x.rowcount) > 0:
				csv = self.x.fetchone()[1]
				actorsList = csv.split(',')
				for actor in actorsList:
					if done == True:
						break
					self.y.execute("""SELECT * FROM `MovieApp`.`Actor_MoviesCSV` WHERE idDirector = (%s)""",  actor)
					if int(self.y.rowcount) > 0:
						csv = self.y.fetchone()[1]
						moviesList = csv.split(',')
						for movie in moviesList:
							if movie not in listMovies and movie not in skipList:
								listMovies.append(movie)
								if len(listMovies) > kMaxSuggestedMovies:
									done = True
									break

		print "Final list: " + str(listMovies)

	def query(self, user, freeText, genres, fromYear, toYear, pageNum):
		"""
			Main query entry point
		"""
		# result to be returned in a dictionaries
		resp = dict()
		#resp["movies"] = self.testGetStatic();
		#resp["movies"] = self.testGetFromYears(fromYear, toYear, pageNum);
		resp["movies"] = self.testGetFromTitle(freeText, pageNum);
		
		#print resp
		return resp;

	def setSeen(self, user, movie):
		print "Addind to seen list for user:" + str(user)
		# add movie to seen
		self.x.execute("""SELECT * FROM `MovieApp`.`User_seen_Movie` WHERE idUser = (%s) and idMovie = (%s)""",  (user, movie))
		numrows = int (self.x.rowcount)
		if numrows<1:
			self.x.execute("INSERT INTO `MovieApp`.`User_seen_Movie` (`idUser`, `idMovie`) VALUES (%s, %s)", (user, movie))
		
	def setQueued(self, user, movie):
		print "Addind to queue list for user:" + str(user)
		# add movie to queued
		self.x.execute("""SELECT * FROM `MovieApp`.`User_queued_Movie` WHERE idUser = (%s) and idMovie = (%s)""",  (user, movie))
		numrows = int (self.x.rowcount)
		if numrows<1:
			self.x.execute("INSERT INTO `MovieApp`.`User_queued_Movie` (`idUser`, `idMovie`) VALUES (%s, %s)", (user, movie))

	def setLiked(self, user, movie, deferCommit = False):
		#print "Addind like for user:" + str(user)
		
		# add movie to user movies likes list
		self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_MoviesCSV` WHERE idUser = (%s)""",  user)
		numrows = int (self.x.rowcount)
		newLike = False
		if numrows<1:
			self.x.execute("INSERT INTO `MovieApp`.`User_liked_MoviesCSV` (`idUser`, `movies`) VALUES (%s, %s)", (user, str(movie)))
			newLike = True
		else:
			csv = self.x.fetchone()[1]
			moviesList = csv.split(',')
			if movie not in moviesList:
				newLike = True
				newMoviesCSV = csv + "," + str(movie)
				#print "adding" + newMoviesCSV 
				self.x.execute("UPDATE `MovieApp`.`User_liked_MoviesCSV` SET movies=%s  WHERE idUser = (%s)""",  (newMoviesCSV, user))
		
		if newLike:
			# let's store it multi-multi too
			self.x.execute("INSERT INTO `MovieApp`.`User_liked_Movie` (`idUser`, `idMovie`) VALUES (%s, %s)", (user, movie))
		
			#
			# ----> Now update directors likes
			#

			# first get all directors for this movie
			self.x.execute("""SELECT * FROM `MovieApp`.`Movie_DirectorsCSV` WHERE idMovie = (%s)""", (movie))
			numrows = int (self.x.rowcount)
			if numrows>0:
				# sometime there is no director bound...
				csv = self.x.fetchone()[1]
				movieDirectorsList = csv.split(',')
				#print "Directors for this movie: " + str(movieDirectorsList)

				# then get current user list of liked directors
				userDirectorsList = []
				userDirectorsCSV = ""
				self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_DirectorsCSV` WHERE idUser = (%s)""",  user)
				numrows = int (self.x.rowcount)
				if numrows>0:
					userDirectorsCSV = self.x.fetchone()[1]
					userDirectorsList = userDirectorsCSV.split(',')
				# then add each movie director, if not liked yet
				for movieDirector in movieDirectorsList:
					if movieDirector not in userDirectorsList:
						userDirectorsCSV = userDirectorsCSV + "," + movieDirector
				#print "New likes CSV for current user: " + userDirectorsCSV
				if numrows>0:
					self.x.execute("UPDATE `MovieApp`.`User_liked_DirectorsCSV` SET directors=%s  WHERE idUser = (%s)""",  (userDirectorsCSV, user))
				else:
					self.x.execute("INSERT INTO `MovieApp`.`User_liked_DirectorsCSV` (`idUser`, `directors`) VALUES (%s, %s)", (user, userDirectorsCSV))


			# ----> Now update actors likes
			#

			# first get all actors for this movie
			self.x.execute("""SELECT * FROM `MovieApp`.`Movie_ActorsCSV` WHERE idMovie = (%s)""", (movie))
			numrows = int (self.x.rowcount)
			if numrows>0:
				# sometime there is no actor bound...
				csv = self.x.fetchone()[1]
				movieActorsList = csv.split(',')
				#print "Actors for this movie: " + str(movieActorsList)

				# then get current user list of liked actors
				userActorsList = []
				userActorsCSV = ""
				self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_ActorsCSV` WHERE idUser = (%s)""",  user)
				numrows = int (self.x.rowcount)
				if numrows>0:
					userActorsCSV = self.x.fetchone()[1]
					userActorsList = userActorsCSV.split(',')
				# then add each movie actor, if not liked yet
				for movieActor in movieActorsList:
					if movieActor not in userActorsList:
						userActorsCSV = userActorsCSV + "," + movieActor
				#print "New likes CSV for current user: " + userActorsCSV
				if numrows>0:
					self.x.execute("UPDATE `MovieApp`.`User_liked_ActorsCSV` SET actors=%s  WHERE idUser = (%s)""",  (userActorsCSV, user))
				else:
					self.x.execute("INSERT INTO `MovieApp`.`User_liked_ActorsCSV` (`idUser`, `actors`) VALUES (%s, %s)", (user, userActorsCSV))

			# ----> Now update movies likes
			#

			# first get all genres for this movie
			self.x.execute("""SELECT * FROM `MovieApp`.`Movie_GenresCSV` WHERE idMovie = (%s)""", (movie))
			numrows = int (self.x.rowcount)
			if numrows>0:
				# sometime there is no genre bound...
				csv = self.x.fetchone()[1]
				movieGenresList = csv.split(',')
				#print "Genres for this movie: " + str(movieGenreList)

				# then get current user list of liked genres
				userGenresList = []
				userGenresCSV = ""
				self.x.execute("""SELECT * FROM `MovieApp`.`User_liked_GenresCSV` WHERE idUser = (%s)""",  user)
				numrows = int (self.x.rowcount)
				if numrows>0:
					userGenresCSV = self.x.fetchone()[1]
					userGenresList = userGenresCSV.split(',')
				# then add each movie genre, if not liked yet
				for movieGenre in movieGenresList:
					if movieGenre not in userGenresList:
						userGenresCSV = userGenresCSV + "," + movieGenre
				#print "New likes CSV for current user: " + userGenresCSV
				if numrows>0:
					self.x.execute("UPDATE `MovieApp`.`User_liked_GenresCSV` SET genres=%s  WHERE idUser = (%s)""",  (userGenresCSV, user))
				else:
					self.x.execute("INSERT INTO `MovieApp`.`User_liked_GenresCSV` (`idUser`, `genres`) VALUES (%s, %s)", (user, userGenresCSV))

	
		if deferCommit == False:
			self.conn.commit()



	"""
		TEST PROCEDURES
	"""

	"""
		TEST 0: static response
	"""
	def testGetStatic(self):
		movieItems = dict()
		movie = dict()
		movie["id"] = "1111"
		movie["title"] = "La professoressa insegna latino"
		movie["plot"] = "Molto significativo"
		movieItems["1111"] = movie;
		movie = dict()
		movie["id"] = "3332"
		movie["title"] = "Corazzata"
		movie["plot"] = "Divertente il secondo tempo"
		movieItems["3332"] = movie;
		return movieItems
	
	"""
		TEST 1: get candidates in the years frame
  		 	- no filtering
			- no sorting
	"""
	def testGetFromYears(self, fromYear, toYear, pageNum):
		movieItems = dict()
		self.x.execute("""SELECT * FROM `MovieApp`.`Movie` WHERE year >= (%s) AND year <= %s LIMIT %s OFFSET %s""",  (fromYear, toYear, self.pageSize, self.pageSize * pageNum))
		for row in self.x:
			#print row
			movie = dict()
			movie["id"] = row[0]
			movie["title"] = row[1]
			movie["plot"] = row[2]
			movie["img"] = row[6]
   	 		movieItems[row[0]] = movie;
		return movieItems;

	"""
		TEST 2: get candidates matching the name pattern as movie title
  		 	- no filtering
			- no sorting
	"""
	def testGetFromTitle(self, freeText, pageNum):
		movieItems = dict()
		sql='SELECT * FROM MovieApp.Movie WHERE title LIKE %s LIMIT %s OFFSET %s'
		args=[freeText+'%', self.pageSize, self.pageSize * pageNum]
		self.x.execute(sql, args)
		for row in self.x:
			#print row
			movie = dict()
			movie["id"] = row[0]
			movie["title"] = row[1]
			movie["plot"] = row[2]
			movie["img"] = row[6]
   	 		movieItems[row[0]] = movie;
		return movieItems;

