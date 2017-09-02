#!/usr/bin/python

import MySQLdb
import sys

# connect to the movie app DB
conn = MySQLdb.connect( host="127.0.0.1", port=3306,
                  user="root",
                  passwd="andrea79",
                  db="MovieApp")
                 
# get cursor 
x = conn.cursor()

# print "Adding movie: " +  title
try:
      print "Deleting users..."
      x.execute("""TRUNCATE TABLE `MovieApp`.`User`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_MatchingMovies`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_liked_Movie`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_liked_MoviesCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_liked_DirectorsCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_liked_ActorsCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_liked_GenresCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_seen_MoviesCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User_queued_MoviesCSV`""")
      conn.commit()
      print "Done !"
except:
      conn.rollback()
      sys.exit()
      print "Error!"
	
conn.close()
