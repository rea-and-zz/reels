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

# get engine
engine = reelsEngine.reelsEngine()

for i in range(10000): 
	# insert 10000 test usrs
	print "Creating user: " + str(i)
	x.execute("INSERT INTO `MovieApp`.`User` (`idUser`, `name`, `email`) VALUES (%s, %s, %s)", (i, str(i)+"-name", str(i)+"-email"  ))
	# for each user, let's create 100 random movie likes
	for j in range(200):
		likedId = random.randint(1,250000)
		#print "Setting random like for: " + str(likedId) 
		if j % 100 == 0:
			engine.setLiked(i, likedId)
		else:
			engine.setLiked(i, likedId, True)

	#if i % 500 == 0:
    #		print "Users added so far: " + str(i)
	conn.commit()

conn.commit()
conn.close()
