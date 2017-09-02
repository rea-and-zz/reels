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
      print "Deleting all.."
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Genre`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Celebrity`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_Genre`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_GenresCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_Actor`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_Director`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Director_MoviesCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Actor_MoviesCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_DirectorsCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`Movie_ActorsCSV`""")
      x.execute("""TRUNCATE TABLE `MovieApp`.`User`""")
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

