# This Python script was written using Python 2.7.13

from __future__ import division
import math
import json

intersectionsCache = {}
correlationCache = {}

# data in format: MovieID,UserID,Rating
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

# convert a line of data into a Rating object
def convertDataLineToRating(line):
  data = [x.strip() for x in line.split(',')]
  return Rating(data[0], data[1], int(float(data[2])))

def getRatingForMovieId(ratingsList, movieId):
  for rating in ratingsList:
    if movieId == rating.getMovieId():
      return rating
  return

def calcMeanRating(userRatings):
  meanRating = reduce(lambda x,y: x + y, list(map(lambda x: x.getRating(), userRatings))) / len(userRatings)
  return meanRating

# dict that we will build out where userId maps to mean rating by that user
def calcUserMeanRatings():
  userMeanRatings = {}
  for userRatings in ratingsByUser.iteritems():
    userMeanRatings[userId] = calcMeanRating(userRatings[1])
  return userMeanRatings

# Get intersection of two users
def getRatingsIntersectionOfUsers(userA, userI):
  """ Builds out a dict of movie ids that each map to an object containing the ratings by each user
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
  # both permuations of possible cache keys for these two users
  cacheKey = userA + userI
  cacheKey2 = userI + userA
  
  # return intersection if already in cache
  if cacheKey in intersectionsCache:
    return intersectionsCache[cacheKey]
  elif cacheKey2 in intersectionsCache:
    return intersectionsCache[cacheKey2]

  intersectionDict= {}
  # if either user doesn't have any ratings in training set the intersection is empty
  if (userA in ratingsByUser and userI in ratingsByUser):
    userA_ratings = ratingsByUser[userA]
    userI_ratings = ratingsByUser[userI]

    for userA_rating in userA_ratings:
      movieId = userA_rating.getMovieId()
      userI_rating = getRatingForMovieId(userI_ratings, movieId)
      if(userI_rating):
        intersectionDict[movieId] = {}
        intersectionDict[movieId][userA] = userA_rating.getRating()
        intersectionDict[movieId][userI] = userI_rating.getRating()

  intersectionsCache[cacheKey] = intersectionDict
  return intersectionDict

# calculate correlation betwen two users
def calcCorrelation(userA, userI):
  # both permuations of possible cache keys for these two users
  cacheKey = userA + userI
  cacheKey2 = userI + userA

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

def calcPredictedRating(userId, movieId):
  userMeanRating = 0
  sum = 0
  sumOfWeights = 0
  if (userId in meanRatings):
    userMeanRating = meanRatings[userId]

  # set of all other user ratings on this movie
  nSet = []
  if movieId in ratingsByMovie:
    nSet = ratingsByMovie[movieId]
  n = len(nSet)

  for rating in nSet:
    i_userId = rating.getUserId()
    correlation = calcCorrelation(userId, i_userId)
    sumOfWeights += abs(correlation)
    sum += (correlation * (rating.getRating() - userMeanRating))

  # define our normalizing constant such that it causes the absolute values of the weights to sum to unity
  k = 0
  if (sumOfWeights > 0):
    k = 1 / sumOfWeights
  return (userMeanRating + (k * sum))

def calcMeanAbsoluteError(results):
  n = len(results)
  sum = 0
  for i in results:
    sum += abs(i['prediction'] - i['trueValue'])
  return sum / n

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

    if userId not in ratingsByUser:
      ratingsByUser[userId] = []

    if movieId not in ratingsByMovie:
      ratingsByMovie[movieId] = []

    ratingsByUser[userId].append(rating)
    ratingsByMovie[movieId].append(rating)

# dict that contains mean rating for each user 
meanRatings = calcUserMeanRatings()

# make predictions and store in results list
# results[i] = {prediction: x, trueValue: y}
results = []
with open('netflix_data/TestingRatings_small.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLineToRating(line)
    predictedRating = calcPredictedRating(rating.getUserId(), rating.getMovieId())
    results.append({'prediction': predictedRating, 'trueValue': rating.getRating()})

meanAbsoluteError = calcMeanAbsoluteError(results)
rootMeanSquareError = calcRootMeanSquareError(results)

# save predictions results and error results to file
outfile = open('results.txt','w')
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

# reset testing ratings list so that in this stage we only run the extra credit tests
myUserId = '9999999'
ratingsByUser[myUserId] = []

with open('netflix_data/TrainingRatings_extraCredit.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLineToRating(line)
    movieId = rating.getMovieId()
    ratingsByUser[myUserId].append(rating)

    if movieId not in ratingsByMovie:
      ratingsByMovie[movieId] = []
    ratingsByMovie[movieId].append(rating)

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
outfile_extraCredit = open('results_extraCredit.txt','w')
outfile_extraCredit.write(json.dumps(results_extraCredit))
outfile_extraCredit.close()

print 'Extra Credit Predictions Complete'