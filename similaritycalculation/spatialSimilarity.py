import os
import sys
from math import *

# add local modules folder
file_path = '../Python_Modules'
sys.path.append(file_path)

from osgeo import gdal, ogr, osr

def spatialOverlap(bboxA, bboxB):
    boxA = _generateGeometryFromBbox(bboxA)
    boxB = _generateGeometryFromBbox(bboxB)

    print(boxA)

    areaA = boxA.GetArea()
    areaB = boxB.GetArea()

    if (areaA == 0) and (areaB == 0):
        bufferDist = 328 # foot
        boxA = boxA.Buffer(bufferDist)
        boxB = boxB.Buffer(bufferDist)

        areaA = boxA.GetArea()
        areaB = boxB.GetArea()

    print(areaA)

    largerArea = areaA if areaA >= areaB else areaB

    intersection = boxA.Intersection(boxB)
    intersectGeometry = ogr.CreateGeometryFromWkt(intersection.ExportToWkt())

    intersectArea = intersectGeometry.GetArea()

    print(intersectArea)

    reachedPercentArea = intersectArea*100/largerArea

    reachedPercentArea = floor(reachedPercentArea * 100)/100
    print(reachedPercentArea)
    return reachedPercentArea


def similarArea(bboxA, bboxB):
    boxA = _generateGeometryFromBbox(bboxA)
    boxB = _generateGeometryFromBbox(bboxB)

    print(boxA)

    areaA = boxA.GetArea()
    areaB = boxB.GetArea()

    print(areaA)
    print(areaB)

    reachedPercentArea = 0
    if areaA >= areaB:
        reachedPercentArea = areaB*100/areaA
    else:
        reachedPercentArea = areaA*100/areaB

    reachedPercentArea = floor(reachedPercentArea*100)/100
    print(reachedPercentArea)


    return reachedPercentArea


def spatialDistance(bboxA, bboxB):
    distBetweenCenterPoints = None
    longerDistance = None
    if (bboxA[0] == bboxA[2]) and (bboxB[0] == bboxB[2]) and (bboxA[1] == bboxA[3]) and (bboxB[1] == bboxB[3]):
        distBetweenCenterPoints = _getDistance((bboxA[0], bboxA[1]),(bboxB[0], bboxB[1]))
        longerDistance = 5

    else:
        if (bboxA[0] == bboxA[2]) and (bboxA[1] == bboxA[3]):
            centerA = ogr.CreateGeometryFromWkt("POINT (%f %f)" % (bboxA[0], bboxA[1]))
        else:
            centerA = _getMidPoint(bboxA)

        if (bboxB[0] == bboxB[2]) and (bboxB[1] == bboxB[3]):
            centerB = ogr.CreateGeometryFromWkt("POINT (%f %f)" % (bboxB[0], bboxB[1]))
        else:
            centerB = _getMidPoint(bboxB)

        type1 = centerA.GetGeometryName()
        type2 = centerB.GetGeometryName()
        print(type1, type2)

        distA = _getDistance((bboxA[1], bboxA[0]), (bboxA[3], bboxA[2]))
        distB = _getDistance((bboxB[1], bboxB[0]), (bboxB[3], bboxB[2]))

        print(distA, distB)

        longerDistance = distA if distA >= distB else distB

        print(longerDistance)

        distBetweenCenterPoints = _getDistance((centerA.GetY(), centerA.GetX()),(centerB.GetY(), centerB.GetX()))
        print(distBetweenCenterPoints)

    if distBetweenCenterPoints != None and longerDistance != None:
        distPercentage = (1 - (distBetweenCenterPoints/longerDistance)) * 100
        distPercentage = floor(distPercentage * 100)/100
        print(distPercentage if distPercentage>0 else 0)
        return distPercentage if distPercentage>0 else 0
    else:
        print("Error while processing")
        return 0



def _generateGeometryFromBbox(bbox):
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    target = osr.SpatialReference()
    target.ImportFromEPSG(2927)

    boxA = ogr.CreateGeometryFromJson("""{
            "type":"Polygon",
            "coordinates":[
                [
                    [
                        %f,%f
                    ],
                    [
                        %f,%f
                    ],
                    [
                        %f,%f
                    ],
                    [
                        %f,%f
                    ],
                    [
                        %f,%f
                    ]
                ]
            ]
        }""" % (bbox[0],bbox[1], bbox[0], bbox[3], bbox[2], bbox[3], bbox[2], bbox[1], bbox[0], bbox[1]))

    
    transform = osr.CoordinateTransformation(source, target)
    boxA.Transform(transform)

    return boxA

def _getDistance(startingpoint, endpoint):
    """
    input: in WGS84 - startingpoint[lat, lon], endpoint[lat, lon]
    """
    # @see http://www.movable-type.co.uk/scripts/latlong.html
    radius = 6371
    radLat1 = (startingpoint[0] * pi) / 180
    radLat2 = (endpoint[0] * pi) / 180
    deltLat = ((endpoint[0] - startingpoint[0]) * pi ) / 180
    deltLon = ((endpoint[1] - startingpoint[1]) * pi ) / 180

    a = sin(deltLat / 2) * sin(deltLat / 2) + cos(radLat1) * cos(radLat2) * sin(deltLon / 2) * sin(deltLon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c
    # print(d)
    return d

def _getMidPoint(bbox):
    line1 = "LINESTRING (%f %f, %f %f)" % (bbox[0], bbox[1], bbox[2], bbox[3])
    line2 = "LINESTRING (%f %f, %f %f)" % (bbox[2], bbox[1], bbox[0], bbox[3])

    line1 = ogr.CreateGeometryFromWkt(line1)
    line2 = ogr.CreateGeometryFromWkt(line2)

    intersectionPoint = line1.Intersection(line2)
    z = intersectionPoint.ExportToWkt()
    intersectGeometry = ogr.CreateGeometryFromWkt(intersectionPoint.ExportToWkt())

    datatype = intersectGeometry.GetGeometryName()

    if str.upper(datatype) == "LINESTRING":
        if bbox[1] == bbox[3]:
            line1 = "LINESTRING (%f %f, %f %f)" % (bbox[0], bbox[1]-0.001, bbox[2], bbox[3]+0.001)
            line2 = "LINESTRING (%f %f, %f %f)" % (bbox[2], bbox[1]-0.001, bbox[0], bbox[3]+0.001)

        elif bbox[0] == bbox[2]:
            line1 = "LINESTRING (%f %f, %f %f)" % (bbox[0]-0.001, bbox[1], bbox[2]+0.001, bbox[3])
            line2 = "LINESTRING (%f %f, %f %f)" % (bbox[2]-0.001, bbox[1], bbox[0]+0.001, bbox[3])

        line1 = ogr.CreateGeometryFromWkt(line1)
        line2 = ogr.CreateGeometryFromWkt(line2)

        intersectionPoint = line1.Intersection(line2)
        intersectGeometry = ogr.CreateGeometryFromWkt(intersectionPoint.ExportToWkt())

        datatype2 = intersectGeometry.GetGeometryName()


    return intersectGeometry

# Geometry
# bbox1 = [13.0078125, 50.62507306341435, 5.44921875, 45.82879925192134]
# bbox2 = [17.7978515625, 52.09300763963822, 7.27294921875, 46.14939437647686]
# spatialDistance(bbox1, bbox2)

# Points
# bbox1 = [11.0078125, 50.62507306341435, 11.0078125, 50.62507306341435]
# bbox2 = [13.0082125, 50.62513301341435, 13.0082125, 50.62513301341435]
# spatialDistance(bbox1, bbox2)

# Polygon and Point
# bbox1 = [11.0078125, 50.62507306341435, 13.0078125, 50.62507306341435]
# bbox2 = [13.0082125, 50.62513301341435, 13.0082125, 50.62513301341435]
# spatialDistance(bbox1, bbox2)

