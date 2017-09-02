#!/usr/bin/python
# coding: utf_8

import reelsEngine
import sys
from flask import json

page = 0
if len(sys.argv) > 1:
	page = int(sys.argv[1])

engine = reelsEngine.reelsEngine()

#res = engine.query("2323", "La", "gen", 2008, 2009, page)

"""
user = 10
val = 46000
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
engine.setLiked(user, val)
val = val + 10
"""

engine.getSuggestion(100)

#engine.getMovieInfo(261713)

#js = json.dumps(res)
#print js
