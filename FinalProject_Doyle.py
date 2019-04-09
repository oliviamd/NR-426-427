#Olivia Doyle
#NR 426: Final Project
#Project Description: This script will create a layer of possible areas for reintroduction of black footed ferrets in Colorado.
#These areas will be based on these parameters:
    #In Grassland ecosystems
    #Away from disturbance: 1 mile from roads and 5 miles from cities
    #Within prairie dog habitat (food source)


#import arcpy and set enviornment to where the data is saved
import arcpy
arcpy.env.workspace = r"E:\NR426\Final Project\ProjectData"
print("Workspace has been set as: " + arcpy.env.workspace)

#Extract by Attributes is a Spatial Analyst tool so we need to import sa before starting to run the tool
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
print("Spatial analyst extension has been checked out")
#Allow data to be overwritten if it already exists
arcpy.env.overwriteOutput = True

#Step 1: Extract by Attributes to extract only the grassland cover from the NLCD landcover layer
#ALSO: mask grasslands to prairie dog range
print("                 ##### STEP ONE #####")

#Check that the data exists
landcover= r"E:\NR426\Final Project\ProjectData\land_cover"
if arcpy.Exists(landcover + r"\nlcd_co_utm13.tif"):
    print("landcover data layer exists")
else:
    print ("does not exist")
#set local variables
input_raster= landcover+ r"\nlcd_co_utm13.tif"
where_clause= "VALUE = 71"
#try to run the Extract by Attributes tool
#if it doesnt work, print the error
try:
# use environment setting to mask the Grasslands.tif layer to the PrairieDogRange layer
    arcpy.env.mask= r"E:\NR426\Final Project\ProjectData\FerretProjectData.gdb\PrairieDogRange"
    print("extracting values.......")
    extractGrasslands= arcpy.sa.ExtractByAttributes(input_raster, where_clause)
    print("saving output to: " + arcpy.env.workspace)
    extractGrasslands.save(r"E:\NR426\Final Project\ProjectData\Grasslands.tif")
    print("values have been extracted")
    print("new layer is called: Grasslands.tif")
#Step2: Clip Cities layer to pdog range and dissolve to create multipart features
#make sure the cities layer exists
    print("                 ##### STEP TWO #####")
    if arcpy.Exists(r"E:\NR426\Final Project\ProjectData\MuniBounds.shp"):
        print("Cities layer exists")
    else:
        print("Cities layer does NOT exist :(")
#set local variables for clip tool and run tool
    infeatures=r"E:\NR426\Final Project\ProjectData\MuniBounds.shp"
    clipfeatures= r"E:\NR426\Final Project\ProjectData\FerretProjectData.gdb\PrairieDogRange"
    outfc= arcpy.env.workspace + "\CitiesWithinPDRange"
    print("Clipping cities to prairie dog range......")
    arcpy.Clip_analysis(infeatures, clipfeatures, outfc, "")
    print("Clip successful! New layer is called: CitiesWithinPDRange.shp")
#Perform a dissolve on the clipped cities layer
#set variables for dissolve tool
    inputfeatures= arcpy.env.workspace + "\CitiesWithinPDRange.shp"
    outputfeatures= arcpy.env.workspace + "\CitiesWithinPDRange_Dissolved.shp"
    multipart= "MULTI_PART"
    print("Dissolving CitiesWithinPDRange layer.....")
    arcpy.Dissolve_management(inputfeatures,outputfeatures, "","",multipart,"")
    print("Dissolve successful! New layer is called: CitiesWithinPDRange_Dissolved.shp")
#Step3: Clip roads layer to pdog range layer
    print("                 ##### STEP THREE #####")
#set local variables for clip tool and run tool
    inputfeatures= arcpy.env.workspace + "\CO_Roads_UTM.shp"
    clipfeatures= r"E:\NR426\Final Project\ProjectData\FerretProjectData.gdb\PrairieDogRange"
    outfc= arcpy.env.workspace + "\RoadsWithinPDRange.shp"
    print("Clipping roads layer to prairie dog range......")
    arcpy.Clip_analysis(inputfeatures,clipfeatures,outfc, "")
    print("Clip successful! New layer is called: RoadsWithinPDRange.shp")
#Step4: Buffer the clipped roads layer by 1 mile to indicate area away from disturbance
    print("                 ##### STEP FOUR #####")
#Buffer syntax: Buffer_analysis (in_features, out_feature_class, buffer_distance_or_field, {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field}, {method})
#set local variables for buffer tool and run tool
    in_features= arcpy.env.workspace + "\RoadsWithinPDRange.shp"
    out_feature_class= arcpy.env.workspace + r"\1miBuffer_Roads.shp"
    bufferdistance= "1 Mile"
    line_side= "FULL"
    line_end_type= "ROUND"
    dissolve_option= "ALL"
    dissolve_field= ""
    method= "PLANAR"
    print("Buffering roads layer by 1 mile......")
    arcpy.Buffer_analysis(in_features, out_feature_class ,bufferdistance, line_side, line_end_type, dissolve_option, dissolve_field, method)
    print("Buffer successful! New layer is called 1miBuffer_Roads.shp")
# Step 5: Buffer DISSOLVED cities layer by 5 miles to indicate areas away from disturbance
    print("                 ##### STEP FIVE #####")
#Buffer syntax: Buffer_analysis (in_features, out_feature_class, buffer_distance_or_field, {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field}, {method})
#set local variables for buffer tool and run tool
    in_features= arcpy.env.workspace + "\CitiesWithinPDRange_Dissolved.shp"
    out_feature_class= arcpy.env.workspace + r"\5miBuffer_Cities.shp"
    bufferdistance= "5 Miles"
    line_side= "FULL"
    line_end_type= "ROUND"
    dissolve_field= ""
    method= "PLANAR"
    print("Buffering cities by 5 miles......")
    arcpy.Buffer_analysis(in_features, out_feature_class ,bufferdistance, line_side, line_end_type, dissolve_option, dissolve_field, method)
    print("Buffer successful! New layer is called 5miBuffer_Cities.shp")
#Step 6: Turn NLCD grasslands raster into a polygon with Raster to Polygon conversion tool
#Raster to polygon syntax: RasterToPolygon_conversion (in_raster, out_polygon_features, {simplify}, {raster_field}, {create_multipart_features}, {max_vertices_per_feature})
    print("                 ##### STEP SIX #####")
#set local variables for raster to polygon tool and run tool
    in_raster= arcpy.env.workspace + "\Grasslands.tif"
    out_polygon_features= arcpy.env.workspace + "\Grasslands_polygon.shp"
    simplify= "SIMPLIFY"
    raster_field= "VALUE"
    create_multipart_features= "SINGLE_OUTER_PART"
    max_vertices_per_feature= ""
    print("Running raster to polygon tool......")
    arcpy.RasterToPolygon_conversion(in_raster,out_polygon_features, simplify, raster_field, create_multipart_features, max_vertices_per_feature)
    print("Raster to Polygon tool ran successfully! New layer is called Grasslands_polygon.shp")
#Step 7: run the Union tool to make the cities and roads buffer layers one layer
#Union syntax: Union_analysis (in_features, out_feature_class, {join_attributes}, {cluster_tolerance}, {gaps})
    print("                 ##### STEP SEVEN #####")
#set local variables for Union tool and run tool
    in_features= [arcpy.env.workspace + r"\1miBuffer_Roads.shp", arcpy.env.workspace + r"\5miBuffer_Cities.shp"]
    out_feature_class= arcpy.env.workspace + "\City_Roads_Union.shp"
    join_attributes= "ALL"
    cluster_tolerance= ""
    gaps= "GAPS"
    print("Running Union tool......")
    arcpy.Union_analysis(in_features, out_feature_class, join_attributes, cluster_tolerance, gaps)
    print("Union tool ran successfully! New layer is called City_Roads_Union.shp")
#Step 8: Run erase tool to erase the City_Roads_Union layer to indicate areas away from disturbance only
#erase syntax: Erase_analysis (in_features, erase_features, out_feature_class, {cluster_tolerance})
    print("                 ##### STEP EIGHT #####")
#set local variables for erase tool and run tool
    in_features = arcpy.env.workspace + "\Grasslands_polygon.shp"
    erase_features= arcpy.env.workspace + "\City_Roads_Union.shp"
    out_feature_class= arcpy.env.workspace + "\AreaAwayFromDisturbance.shp"
    cluster_tolerance= ""
    print("Running erase tool......")
    arcpy.Erase_analysis(in_features,erase_features, out_feature_class, cluster_tolerance)
    print("Erase ran successfully! New layer is called AreaAwayFromDisturbance.shp")
    print("                 *****FINAL LAYER CREATED*****")
    print("AreaAwayFromDisturbance.shp is a layer that shows areas suitable for reintroduction of black footed ferrets based on the following parameters: ")
    print("Parameter 1: 5 miles from cities and 1 mile from roads")
    print("Parameter 2: Within prairie dog range (food source)")
    print("Parameter 3: Within grasslands")

    print("                 ***** END OF SCRIPT *****")

except Exception as e:
    print("Error: " +e.args[0])
