# This Python script was written using Python 2.7.13

from __future__ import division
import math
import json

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

# contains a list of Ratings and provides helper functions
class RatingsList:
  def __init__(self):
    self.ratingsList = []

  def getRatingsList(self):
    return self.ratingsList

  def setRatingsList(self, ratingsList):
    self.ratingsList = ratingsList

  # convert a line of data into a Rating object
  def convertDataLineToRating(self, line):
    data = [x.strip() for x in line.split(',')]
    return Rating(data[0], data[1], int(float(data[2])))

  def addRating(self, dataLine):
    rating = self.convertDataLineToRating(dataLine)
    self.ratingsList.append(rating)
    
  def getRatingsListForUser(self, userId):
    userRatings = list(filter(lambda x: x.getUserId() == userId, self.ratingsList))
    ratingsList = RatingsList()
    ratingsList.setRatingsList(userRatings)
    return ratingsList

  def getRatingForMovieId(self, movieId):
    for rating in self.ratingsList:
      if movieId == rating.getMovieId():
        return rating
    return

def calcMeanRating(ratingsList, userId):
  userRatings = ratingsByUser[userId].getRatingsList()
  meanRating = reduce(lambda x,y: x + y, list(map(lambda x: x.getRating(), userRatings))) / len(userRatings)
  return meanRating

# dict that we will build out where userId maps to mean rating by that user
def calcUserMeanRatings(ratings):
  userMeanRatings = {}
  ratingsList = ratings.getRatingsList()
  # for each unique userId found in trainingRatings, calculate mean rating
  for rating in ratingsList:
    userId = rating.getUserId()
    if(userId not in userMeanRatings):
      userMeanRatings[userId] = calcMeanRating(ratingsList, userId)
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
  intersectionDict= {}

  # if either user doesn't have any ratings in training set the intersection is empty
  if (userA in ratingsByUser and userI in ratingsByUser):
    userA_ratings = ratingsByUser[userA]
    userI_ratings = ratingsByUser[userI]

    for userA_rating in userA_ratings.getRatingsList():
      movieId = userA_rating.getMovieId()
      userI_rating = userI_ratings.getRatingForMovieId(movieId)
      if(userI_rating):
        intersectionDict[movieId] = {}
        intersectionDict[movieId][userA] = userA_rating.getRating()
        intersectionDict[movieId][userI] = userI_rating.getRating()

  return intersectionDict

# calculate correlation betwen two users
def calcCorrelation(userA, userI):
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
  if (sqrt_denominator == 0):
    return 0
  else:
    return sum / sqrt_denominator

def calcPredictedRating(userId, movieId):
  userMeanRating = 0
  sum = 0
  sumOfWeights = 0
  if (userId in meanRatings):
    userMeanRating = meanRatings[userId]

  # set of all other user ratings on this movie
  nSet = list(filter(lambda x: x.getMovieId() == movieId, trainingRatings.getRatingsList()))
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

# load and read in data
trainingRatings = RatingsList()
testingRatings = RatingsList()

# Creating a dictionary keyed by user id that will reference the ratings for that user
# Doing this up front so that we don't have to recalculate every time we calculate correlation between 2 users
ratingsByUser = {}

with open('netflix_data/TrainingRatings.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    trainingRatings.addRating(line)
    # get user id just added
    userId = trainingRatings.getRatingsList()[-1].getUserId()
    # make a placeholder in dictionary that we will fill in once all data has been parsed in
    ratingsByUser[userId] = -1

with open('netflix_data/TestingRatings.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    testingRatings.addRating(line)

# build out dict of ratings by each user
for userIdKey in ratingsByUser:
  ratingsByUser[userIdKey] = trainingRatings.getRatingsListForUser(userIdKey)

# dict that contains mean rating for each user 
meanRatings = calcUserMeanRatings(trainingRatings)

# make predictions and store in results list
# results[i] = {prediction: x, trueValue: y}
results = []
for item in testingRatings.getRatingsList():
  predictedRating = calcPredictedRating(item.getUserId(), item.getMovieId())
  print "predicted rating: " + str(predictedRating)
  results.append({'prediction': predictedRating, 'trueValue': item.getRating()})

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

# reset data structures
ratingsByUser = {}
testingRatings = RatingsList() # reset testing ratings list so that in this stage we only run the extra credit tests
myUserId = '9999999'

with open('netflix_data/TrainingRatings_extraCredit.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    trainingRatings.addRating(line)
    # get user id just added
    userId = trainingRatings.getRatingsList()[-1].getUserId()
    # make a placeholder in dictionary that we will fill in once all data has been parsed in
    ratingsByUser[userId] = -1

with open('netflix_data/TestingRatings_extraCredit.txt', 'r') as trainingDataFile:
  for line in trainingDataFile:
    testingRatings.addRating(line)

# only need add one more ratings list for my user
ratingsByUser[myUserId] = trainingRatings.getRatingsListForUser(myUserId)

# only need to calculate one more mean in this step
meanRatings[myUserId] = calcMeanRating(trainingRatings.getRatingsList(), myUserId)

# make predictions and store in results list
# results[i] = {prediction: x, trueValue: y}
results_extraCredit = []
for item in testingRatings.getRatingsList():
  predictedRating = calcPredictedRating(item.getUserId(), item.getMovieId())
  results_extraCredit.append({'movieId': item.getMovieId(), 'prediction': predictedRating, 'trueValue': item.getRating()})

# save predictions results and error results to file
outfile_extraCredit = open('results_extraCredit.txt','w')
outfile_extraCredit.write(json.dumps(results_extraCredit))
outfile_extraCredit.close()

print 'Extra Credit Predictions Complete'