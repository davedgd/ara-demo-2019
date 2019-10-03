import boto3
import pprint
import fnmatch
import os
import re
import numpy as np
import pandas as pd

import time
import progressbar

rekognitionClient = boto3.client(
    'rekognition',
    aws_access_key_id = '...', # set access key
    aws_secret_access_key = '...', # set secret key
    region_name = 'us-east-1'
    )

def TwoFaceSimilarity (image1, image2):
   
    image1 = open(image1, 'rb')
    image2 = open(image2, 'rb')

    response = rekognitionClient.compare_faces(
        SimilarityThreshold = 0,
        SourceImage = {'Bytes': image1.read()},
        TargetImage = {'Bytes': image2.read()}
        )

    # to-do: need to error out if multiple faces/matches are detected
    
    #pprint.pprint(response['FaceMatches'])
    similarity = str(response['FaceMatches'][0]['Similarity'])

    image1.close()
    image2.close()

    return(similarity)

def DetectFaces (image):

    image = open(image, 'rb')

    response = rekognitionClient.detect_faces(
        Image = {'Bytes': image.read()}, 
        Attributes=['ALL'])

    # to-do: need to structure this output
    pprint.pprint(response)

    image.close()

def ListFiles (extension, path = "."):

    extensionRule = re.compile(fnmatch.translate('*.' + extension), re.IGNORECASE)

    return [name for name in os.listdir(path) if extensionRule.match(name)]

def FaceMatrix (fileNames, path, toCSV = True, doComparisons = True):

    numFaces = len(fileNames)

    matrix = np.arange(numFaces ** 2, dtype = np.float).reshape(numFaces, numFaces)

    matrix = np.tril(matrix, k = -1)

    fileNames = np.asarray(fileNames)

    validComparisons = np.nonzero(matrix)

    image1 = fileNames[validComparisons[0]]
    image2 = fileNames[validComparisons[1]]

    print('Total Comparisons:', len(image1))

    comparisons = []

    if doComparisons:
        for i in enumerate(progressbar.progressbar(image1)):
            comparisons.append(TwoFaceSimilarity(os.path.join(path, image1[i]), os.path.join(path, image2[i])))

        for i, similarity in enumerate(comparisons):
            matrix[validComparisons[0][i], validComparisons[1][i]] = similarity

    i_upper = np.triu_indices(matrix.shape[0], k = 0)
    matrix[i_upper] = matrix.T[i_upper]

    np.fill_diagonal(matrix, np.nan)

    df = pd.DataFrame.from_records(matrix)
    df.index = fileNames
    df.columns = fileNames

    return(df)

def WriteFaceMatrix (faceMatrix, file):
    faceMatrix.to_csv(file)

if __name__ == "__main__":

    # note: not used
    #image1 = '...'
    #image2 = '...'
    #print('Similarity:', TwoFaceSimilarity(image1, image2))
    #DetectFaces(image1)
    
    path = 'faces/combined/' # set path to faces for similarity matrix
    fileNames = ListFiles(extension = 'jpg', path = path)
    filePaths = [os.path.join(path, s) for s in fileNames]

    faceMatrix = FaceMatrix(fileNames, path, doComparisons = True)

    WriteFaceMatrix(faceMatrix, file = 'output/faceMatrix - Combined.csv')