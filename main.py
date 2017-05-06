# This Python script was written using Python 2.7.13

from __future__ import division
import math
import json

correlationCache = {}

"""
Class to store and provide access to data for a rating
"""
class Rating:
  def __init__(self, movieId, userId, rating):
    self.movieId = movieId
    self.userId = userId
    self.rating = rating

  def getMovieId(self):
    return self.movieId

  def getUserId(self):
    return self.userId

  def getRating(self):
    return self.rating

"""
Convert a line of data into a Rating object
"""
def convertDataLineToRating(line):
  data = [x.strip() for x in line.split(',')]
  return Rating(data[0], data[1], int(float(data[2])))

"""
Calculate mean rating given a list of ratings
"""
def calcMeanRating(userRatings):
  sum = 0
  n = len(userRatings.keys())
  for item in userRatings.iteritems():
    sum += item[1]
  return (sum / n)

"""
Dict that we will build out where userId maps to mean rating by that user
"""
def calcUserMeanRatings():
  userMeanRatings = {}
  for userRatings in ratingsByUser.iteritems():
    userMeanRatings[userId] = calcMeanRating(userRatings[1])
  return userMeanRatings

""" 
  Calculate intersections of two users
  Builds out a dict of movie ids that each map to an object containing the ratings by each user
  Args:
    userA: Id of first user
    userI: Id of second user

  Return: 
  {
    [movieId]: {
      [userId_A]: [ratingValue]
      [userId_I]: [ratingValue]
    },
    ...
  }
  """
def getRatingsIntersectionOfUsers(userA, userI):
  intersectionDict= {}
  # if either user doesn't have any ratings in training set the intersection is empty
  if (userA in ratingsByUser and userI in ratingsByUser):
    userA_ratings = ratingsByUser[userA]
    userI_ratings = ratingsByUser[userI]

    keys_a = set(userA_ratings.keys())
    keys_i = set(userI_ratings.keys())
    intersection = keys_a & keys_i

    for key in intersection:
      intersectionDict[key] = {}
      intersectionDict[key][userA] = userA_ratings[key]
      intersectionDict[key][userI] = userI_ratings[key]

  return intersectionDict

"""
Calculate correclation between two users
"""
def calcCorrelation(userA, userI):
  # both permuations of possible cache keys for these two users
  cacheKey = userA +  '-' + userI
  cacheKey2 = userI + '-' + userA

  # return correlation if already in cache
  if cacheKey in correlationCache:
    return correlationCache[cacheKey]
  elif cacheKey2 in correlationCache:
    return correlationCache[cacheKey2]

  userA_mean = 0 if not userA in meanRatings else meanRatings[userA]
  userI_mean = 0 if not userI in meanRatings else meanRatings[userI]
  
  # items that both userA and userI have rated
  j_items = getRatingsIntersectionOfUsers(userA, userI)

  sum = 0
  a_squaredSum = 0
  i_squaredSum = 0

  for item in j_items.iteritems():
    values = item[1]

    #get rating of movie by each user
    v_aj = values[userA]
    v_ij = values[userI]

    #subtract mean
    v_aj_minus_mean = v_aj - userA_mean
    v_ij_minus_mean = v_ij - userI_mean

    # calculate sums in various parts of equation
    sum += v_aj_minus_mean * v_ij_minus_mean
    a_squaredSum += v_aj_minus_mean**2
    i_squaredSum += v_ij_minus_mean**2

  sqrt_denominator = math.sqrt(a_squaredSum * i_squaredSum)
  correlation = 0
  if (sqrt_denominator != 0):
    correlation = sum / sqrt_denominator
  
  correlationCache[cacheKey] = correlation
  return correlation

"""
Make prediction given a userId and a movieId
"""
def calcPredictedRating(userId, movieId):
  userMeanRating = 0
  sum = 0
  sumOfWeights = 0
  if (userId in meanRatings):
    userMeanRating = meanRatings[userId]

  # set of all other user ratings on this movie
  nSet = {}
  if movieId in ratingsByMovie:
    nSet = ratingsByMovie[movieId]

  for item in nSet.iteritems():
    i_userId = item[0]
    correlation = calcCorrelation(userId, i_userId)
    sumOfWeights += abs(correlation)
    sum += (correlation * (item[1] - userMeanRating))

  # define our normalizing constant such that it causes the absolute values of the weights to sum to unity
  k = 0
  if (sumOfWeights > 0):
    k = 1 / sumOfWeights
  return (userMeanRating + (k * sum))

"""
Calculate mean absolute error
"""
def calcMeanAbsoluteError(results):
  n = len(results)
  sum = 0
  for i in results:
    sum += abs(i['prediction'] - i['trueValue'])
  return sum / n

"""
Calculate root mean squared error
"""
def calcRootMeanSquareError(results):
  n = len(results)
  sum = 0
  for i in results:
    sum += (i['prediction'] - i['trueValue'])**2
  return math.sqrt(sum / n)

# Load and read in data
# Creating a dictionary keyed by user id that will reference the ratings for that user
# Doing this up front so that we don't have to recalculate every time we calculate correlation between 2 users
# Also creating a dict that contains the ratings by each movie. Doing this so we don't have to filter entire list to get nSet for each movie
ratingsByUser = {}
ratingsByMovie = {}

with open('netflix_data/TrainingRatings.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    # get rating just added, store in dict of ratings by user
    rating = convertDataLineToRating(line)
    userId = rating.getUserId()
    movieId = rating.getMovieId()
    ratingValue = rating.getRating()

    # each entry is a dict of movieId: rating
    if userId not in ratingsByUser:
      ratingsByUser[userId] = {}

    # each entry is a dict of userId: rating
    if movieId not in ratingsByMovie:
      ratingsByMovie[movieId] = {}

    ratingsByUser[userId][movieId] = ratingValue
    ratingsByMovie[movieId][userId] = ratingValue

# dict that contains mean rating for each user 
meanRatings = calcUserMeanRatings()

# make predictions and store in results list
# results[i] = {prediction: x, trueValue: y}
results = []
progressCounter = 0
with open('netflix_data/TestingRatings.txt', 'r') as testingDataFile:
  for line in testingDataFile:
    rating = convertDataLineToRating(line)
    predictedRating = calcPredictedRating(rating.getUserId(), rating.getMovieId())
    results.append({'prediction': predictedRating, 'trueValue': rating.getRating()})
    progressCounter += 1
    if progressCounter % 100 == 0:
      print "Predictions made: " + str(progressCounter)

meanAbsoluteError = calcMeanAbsoluteError(results)
rootMeanSquareError = calcRootMeanSquareError(results)

# save predictions results and error results to file
outfile = open('results.json','w')
outfile.write(json.dumps(results))
outfile.close()

error_outfile = open('error_results.txt','w')
error_outfile.write('Mean Absolute Error: ' + str(meanAbsoluteError))
error_outfile.write('\nRoot Mean Square Error: ' + str(rootMeanSquareError))
error_outfile.write('\n')
error_outfile.close()

print 'Mean Absolute Error: ' + str(meanAbsoluteError)
print 'Root Mean Square Error: ' + str(rootMeanSquareError)
print 'Predictions Complete'

# Extra Credit
# Add my ratings to training set run tests against 
myUserId = '9999999'
ratingsByUser[myUserId] = {}

with open('netflix_data/TrainingRatings_extraCredit.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLineToRating(line)
    ratingValue = rating.getRating()
    movieId = rating.getMovieId()
    ratingsByUser[myUserId][movieId] = ratingValue

    if movieId not in ratingsByMovie:
      ratingsByMovie[movieId] = {}
    ratingsByMovie[movieId][myUserId] = ratingValue

# only need to calculate one more mean in this step
meanRatings[myUserId] = calcMeanRating(ratingsByUser[myUserId])

# make predictions and store in results list
# results[i] = {prediction: x, trueValue: y}
results_extraCredit = []
with open('netflix_data/TestingRatings_extraCredit.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLineToRating(line)
    predictedRating = calcPredictedRating(rating.getUserId(), rating.getMovieId())
    results_extraCredit.append({'movieId': rating.getMovieId(), 'prediction': predictedRating, 'trueValue': rating.getRating()})

# save predictions results and error results to file
outfile_extraCredit = open('results_extraCredit.json','w')
outfile_extraCredit.write(json.dumps(results_extraCredit))
outfile_extraCredit.close()

print 'Extra Credit Predictions Complete'