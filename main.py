from __future__ import division

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
def convertDataLine(line):
  data = [x.strip() for x in line.split(',')]
  return Rating(data[0], data[1], int(float(data[2])))

# TODO: make sure we are getting floating point division
def calcMeanRating(dataset, userId):
  ratingsByUser = list(filter(lambda x: x.getUserId() == userId, dataset))
  meanRating = reduce(lambda x,y: x + y, list(map(lambda x: x.getRating(), ratingsByUser))) / len(ratingsByUser)
  return meanRating

# dict that we will build out where userId maps to mean rating by that user
def calcUserMeanRatings(dataset):
  userMeanRatings = {}
  # for each unique userId found in trainingRatings, calculate mean rating
  for rating in dataset:
    userId = rating.getUserId()
    if(userId not in userMeanRatings):
      userMeanRatings[userId] = calcMeanRating(dataset, userId)
  return userMeanRatings

# calculate correlation betwen two users
def calcCorrelation(userA, userI):
  return 1

def calcPredictedRating(userId, movieId):
  userMeanRating = 0
  k = 1
  sum = 0
  if (userId in meanRatings):
    userMeanRating = meanRatings[userId]

  # set of all other user ratings on this movie
  nSet = list(filter(lambda x: x.getMovieId() == movieId, trainingRatings))
  n = len(nSet)

  for rating in nSet:
    i_userId = rating.getUserId()
    correlation = calcCorrelation(userId, i_userId)
    sum += (correlation * (rating.getRating() - userMeanRating))

  return (userMeanRating + (k * sum))

# load and read in data
trainingRatings = []
testingRatings = []

with open("netflix_data/TrainingRatings_small.txt", "r") as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLine(line)
    trainingRatings.append(rating)

with open("netflix_data/TestingRatings_small.txt", "r") as trainingDataFile:
  for line in trainingDataFile:
    rating = convertDataLine(line)
    testingRatings.append(rating)

# dict that contains mean rating for each user 
meanRatings = calcUserMeanRatings(trainingRatings)


# TODO: make predictions
# TODO: Implement Mean Absolute Error and the Root Mean Squared Error to evaluate predictions

print "Complete"