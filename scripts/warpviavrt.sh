#!/bin/sh

echo "Warping $1 using GCPs in db/rectifier.sqlite..."

export BASE_PATH="."
export MAP_PATH="$BASE_PATH/uploads/maps"
export FILENAME=$1;
export TARGET=$2
export ORDER=$3
export GCPS="`
echo "SELECT x,y,lon,lat 
      FROM main_gcp,main_map 
      WHERE main_gcp.map_id=main_map.id  and 
            main_map.file='maps/$1';" | \
sqlite3 "$BASE_PATH/db/rectifier.db" | \
sed -e 's/|/ /g' -e 's/^/-gcp /'`"
echo $GCPS
export TIME=`date +'%s'`
if [ "$ORDER" = "tps" ]; then
    ORDER="-tps"
elif [ "$ORDER" -gt 0 ]; then
    ORDER="-order $ORDER"
else 
    ORDER=""
fi
if gdalinfo $MAP_PATH/$FILENAME  | grep -Eq "ColorInterp=Pal"; then
    ALPHA="-dstnodata 255"
else
    ALPHA="-dstalpha"
fi
gdal_translate -a_srs '+init=epsg:4326' -of VRT $MAP_PATH/$FILENAME $MAP_PATH/$$.vrt $GCPS 
gdalwarp $ORDER $MAP_PATH/$$.vrt $MAP_PATH/$TARGET $ALPHA -co TILED=YES -co ALPHA=YES
#gdalwarp $ORDER $LIBPATH/maps/$$.vrt $LIBPATH/maps/$TARGET $ALPHA -co TILED=YES -co COMPRESS=PACKBITS -co ALPHA=YES
rm -f $MAP_PATH/$$.vrt
