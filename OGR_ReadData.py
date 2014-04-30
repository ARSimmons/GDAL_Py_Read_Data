###############################################
## Arielle Simmons                           ##
## Data Engineer                             ##
## Tableau Software                          ##
## Date created: January 28, 2013            ##
## Date modified:                            ##
###############################################

## This script reads file information using the
## functions available in the GDAL library (http://www.gisinternals.com/sdk/)
## In order to work, the following steps have to be taken:
## 1. Get the GDAL core files
## 2. Get the Python bindings for the ver. of Python you
##    are running (I am using python 2.7)
## 3. Install GDAL Core files (choose the 'typical' installation)
## 4. Edit Environmental Variables
## 5. Run/Test Python bindings by using 'from osgeo import ogr' and
##    'from osgeo import gdal' in the Python shell...if
##    everything prints then you are good to go!
##    

## The GDAL Core files and bindings (for Python 2.7) can be found
## at the above website. Procedures for modifying the
## Environmental Variables (for Windows XP, & 7) can be found
## at this website:
## http://pythongisandstuff.wordpress.com/2011/07/07/installing-gdal-and-ogr-for-python-on-windows/
## In general, you must make modifications in the 'System Variables' pane
## on the 'Path' variable.

from osgeo import ogr
import fnmatch
import sys
import string
import re
import osr
import os

# To begin, I set the initial directory workspace. "directory" is the initial directory to
# search under,
# WARNING : THIS MUST BE SET BEFORE THE USER BEGINS USING THIS SCRIPT

folder = r'C:\Users\ASimmons\Desktop\Code\OGR_GDAL_ReadData\Sample_Data\pe_StPro'


# This function helps transform the projection file into an EPSG code,
# the function was obtained from a stackoverflow posting here: http://tinyurl.com/ctrc4bx

def wkt2epsg(wkt, epsg=r'C:\Program Files (x86)\GDAL\projlib\epsg', forceProj4=False):


# wkt: WKT definition
# epsg: the proj.4 epsg file (defaults to '/usr/local/share/proj/epsg')
# forceProj4: whether to perform brute force proj4 epsg file check (last resort)

# Returns: EPSG code

       code = None
       p_in = osr.SpatialReference()
       s = p_in.ImportFromWkt(wkt)
       if s == 5:  # invalid WKT
           return None
       if p_in.IsLocal() == 1:
       # this is a local definition
           return p_in.ExportToWkt()
       if p_in.IsGeographic() == 1:
       # this is a geographic srs
           cstype = 'GEOGCS'
       else:
       # this is a projected srs
           cstype = 'PROJCS'
       an = p_in.GetAuthorityName(cstype)
       ac = p_in.GetAuthorityCode(cstype)
       if an is not None and ac is not None:
       # return the EPSG code
           return '%s:%s' % \
               (p_in.GetAuthorityName(cstype), p_in.GetAuthorityCode(cstype))
       else:
       # try brute force approach by grokking proj epsg definition file
           p_out = p_in.ExportToProj4()
           if p_out:
               if forceProj4 is True:
                   return p_out
               f = open(r'C:\Program Files (x86)\GDAL\projlib\epsg')
               for line in f:
                   if line.find(p_out) != -1:
                       m = re.search('<(\\d+)>', line)
                       if m:
                           code = m.group(1)
                           break
               if code:
               # match
                   return 'EPSG:%s' % code
               else:  # no match
                   return 'EPSG: ' ,None
           else:
               return 'EPSG: ' ,None

# Using the os.walk and fnmatch functions, I construct a list of shapefile paths
# to pass in my driver.Open() funtion

pattern = "*.shp"
shpList = []

for path, dirs, files in os.walk(folder):
	for filename in fnmatch.filter(files, pattern):
		shpList.append(os.path.join(path, filename))

# The OGR ESRI Shapefile driver allows us to
# create a directory full of shapefiles, or a single shapefile as a datasource.
# in this statement I set the driver...

driver = ogr.GetDriverByName('ESRI Shapefile')

# and then for each shapefile path in the list I use
# the Driver Open(<filename>,<update>) method to return
# the data source object (also: since update is set to '0'
# it is a Read Only procedure).

# Note: the OGR Shapefile driver treats a whole
# directory of shapefiles as a dataset, and a single shapefile within that
# directory as a layer. However...some of the documentation
# has noted that Open() is unpredictable
# when the directory contains files OTHER then what
# was specified (e.g. 'ESRI Shapefile', 'FileGDB').
# ...it is still possible that the for above loop is NOT
# necessary...will explore when I have more time..


for shp in shpList:
       dataset = driver.Open(shp, 0)
       # command to access the layers in a shapefile  and get field names
       layer = dataset.GetLayer(0)
       feature = layer.GetFeature(0)
       feature2 = layer.GetFeature(1)
       layer_defn = layer.GetLayerDefn()
       field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]

       # get extent as a tuple

       extent = layer.GetExtent()

       # get geometry type, if there is one
       
       geometry = feature.GetGeometryRef()
       if geometry is not None:
              geo_type = geometry.GetGeometryName()

       # get some sample data
       feature1_items = feature.items()
       
       # get some sample data
       # if there is a second feature, get it
       if feature2 is not None:
              feature2_items = feature2.items()


       
       # print command
       print "##### BEGIN RECORD #####"
       # print name of shapefile
       base=os.path.basename(shp)
       base=os.path.splitext(base)[0]
       print 'Dataset Name: ' + base
       # print relative path
       relpath = shp
       common_prefix = 'C:\Users\ASimmons\Desktop\Code\OGR_GDAL_ReadData'
       relative_paths = [os.path.relpath(path, common_prefix)]
       print "Dataset Path: .\\","\\".join(relative_paths)
       numFeatures = layer.GetFeatureCount()
       print 'Number of Features: ' + str(numFeatures)
       if geometry is not None:
              print 'Geometry Type: ' , geo_type
       else:
              print 'Geometry Type: ' + "NO GEOMETRY"
       print 'Fields: ' , field_names
       print 'Extent: ' , extent
 #      print 'Upper Left: ', extent[0], extent[3]
 #      print 'Lower Right: ', extent[1], extent[2]
       numFeatures = layer.GetFeatureCount() 
       # Read and print the projection information of the shapefile
       # Note: If the shapefile doesn't have a .prj, it doesn't include SRS info!\
       try:
              spatialRef = layer.GetSpatialRef().ExportToWkt()
              print "WKT spatial reference:   %s" % (spatialRef)
              # use the function wkt2epsg to print epsg code, if possible
              print wkt2epsg(spatialRef)
       except:
              print "WKT spatial reference: NULL - THIS FEATURE HAD NO SRS"
       print 'Sample Values: '
       print feature1_items
       if feature2 is not None:
              print feature2_items
       print "##### END RECORD #####"
       print " "

if dataset is None:
       print 'Could not open ' + shp
       sys.exit(1)





        

