var currentMapData = null;
var features = [];
var featuresArray = [];
var userMap = null;
var markers = null;
var gcpBeingEdited = null;
var filename = null;
var refMap = null;
var refMarkers = null;
var IMAGE_BASE = "../uploads/";
var API_PATH = "../api.cgi";
var WMS_PATH = "../wms.cgi";
var warpedWMSLayer = null; 
var geocodeMarker;
function addRefLayer() {
    var userlayer = null;
    if ($('layertype').value == "WMS") {
        userlayer = new OpenLayers.Layer.WMS("User Added", $('layerurl').value);
    } else {
        userlayer = new OpenLayers.Layer.KaMap("User Added", $('layerurl').value);
    }
    refMap.addLayer(userlayer);
    refMap.setBaseLayer(userlayer);
    $('layerurl').value = "";
    $('layerAdder').style.display="none";
}

function createGcp(userLonLat) {
    var feat = new OpenLayers.Feature(markers, userLonLat);
    var id   = feat.id;
    features[id] = feat;
    featuresArray.push(feat);

    var marker = feat.createMarker();
    marker.events.register("click", feat, toggleLocationPopup);  
    markers.addMarker(marker);
    var popup = feat.createPopup();
    popup.setBackgroundColor("lightyellow");
    popup.setSize(new OpenLayers.Size(200, 40));
    popup.setContentHTML(
      '<img src="../static/close.gif" style="float:right" onclick="toggleLocationPopup({}, \''+id+'\')" />'
      + '<span id="' + id + '_Input"></span>'
      + ' <a href="" onclick="return removeLocation(\''+ id + '\')">remove</a>'
       );
    setCurrentGCP(id);  
    popup.events.register("click", userMap, function (e) {
                                        Event.stop(e); return false;});
    popup.hide();
    userMap.addPopup(popup);
    return id;
}    

function addGCP(evt) {
    var pt   = userMap.getLonLatFromPixel(evt.xy);
    var id = createGcp(pt); 
    toggleLocationPopup(evt, id);
} 

function setCurrentGCP(id) {
    gcpBeingEdited = id;
}    

function pushTD (tr, innerHTML, id) {
    var td = document.createElement("td");
    td.innerHTML = innerHTML;
    if (id) {
        td.id = id;
    }    
    tr.appendChild(td);
}

function modifyGCPEvent(evt) {
    if (gcpBeingEdited != null) {
        var pt   = refMap.getLonLatFromPixel(evt.xy);
        modifyGCP(pt);
        var feat = features[gcpBeingEdited];
        var data = { 
                     'lon': pt.lon,
                     'lat': pt.lat,
                     'x': feat.lonlat.lon,
                     'y': userMap.maxExtent.top - feat.lonlat.lat,
                     'handler': 'updateData'
                   };
        if (feat.gcpId) { 
            data.gcp = feat.gcpId;
        }    
        addScript(API_PATH+"/add/"+filename+"?" + 
                  OpenLayers.Util.getParameterString(data), 
                  feat.gcpId ? "Updating "+feat.gcpId :
                               "Adding GCP");  
    }
}    
function updateData(data) {
    var table = $('gcpTable');
    for(var i = 0; i < data.gcps.length; i++) {
        var tr = table.childNodes[i+2];
        if (!tr) { 
            table.appendChild(document.createElement('tr'));   
            tr = table.childNodes[i+2];
        }    
        featuresArray[i].gcpId = data.gcps[i][5];
        tr.childNodes[0].innerHTML = '<a href="#" onclick="toggleLocationPopup({},\''+featuresArray[i].id+'\');return false;">'+data.gcps[i][5]+'</a>';;
        tr.childNodes[1].innerHTML = data.gcps[i][0].toFixed(6);
        tr.childNodes[2].innerHTML = data.gcps[i][1].toFixed(6);
        tr.childNodes[3].innerHTML = data.gcps[i][2].toFixed(2);
        tr.childNodes[4].innerHTML = data.gcps[i][3].toFixed(2);
        // tr.childNodes[5].innerHTML = (111000 * Math.sqrt(data.gcps[i][4])).toFixed(2);
        tr.childNodes[5].innerHTML = Math.sqrt(data.gcps[i][4]).toFixed(1);
        tr.id = 'Table_'+featuresArray[i].id;
    }
    if (data.warped) {
        var whtml = "";
        whtml += "Warped Image: <br />"+
        '<ul>'+
        '<li><a href="'+IMAGE_BASE+data.warped+'">Download GeoTIFF (May Be Large!)</a></li>';
	if (data.warped_width && data.warped_height) {
            whtml += '<li><a href="'+WMS_PATH+'?coverage=image&id='+data.id+'&request=GetCoverage&version=1.0.0&service=WCS&CRS=EPSG:4326&format=JPEG2000&width='+data.warped_width+'&height='+data.warped_height+'">Download JPEG 2000</a></li>';
	}    
        whtml += '<li><a href="'+WMS_PATH+'?id='+data.id+'">WMS/WCS URL</a>' +
                     ' (Good for use with OpenLayers)</li>'+
        '</ul>';
	$('warped').innerHTML = whtml;
        if (refMap.layers.length == 7) {
            addWarpedWMSLayer(data.warped);
        } else {
            warpedWMSLayer.mergeNewParams({'image':data.warped});
        }    
    }    
    if (data.error) {
        $('totalError').innerHTML = data.error.toFixed(3);
    }
    if (data.title) {
        $('mapinfo').innerHTML = "<b>"+data.title+"</b>: "+data.description.substr(0,200); if (data.description.length > 200) { $('mapinfo').innerHTML += "..."; }
        $('mapinfo').innerHTML += " <a href='../map/"+filename+"'>(more)</a>";
    }
    currentMapData = data;
    $("status").innerHTML = "";
} 

function modifyGCP(pt) {
    var marker = new OpenLayers.Marker(pt);
    refMarkers.addMarker(marker);
    
    var feat = features[gcpBeingEdited];
    feat.data.gcplonlat = pt;
    if (feat.data.refMarker)
        refMarkers.removeMarker(feat.data.refMarker);
    feat.data.refMarker = marker;
    $(feat.id+'_Input').innerHTML = pt.lon.toFixed(5) + ", " + pt.lat.toFixed(5); 

    marker.events.register("click", feat, function (e) {
        toggleLocationPopup(e, this.id); 
    });
    var tr = null; 
    if (!$('Table_'+feat.id)) { 
        tr = document.createElement("tr");
        tr.id='Table_'+feat.id;
        $('gcpTable').appendChild(tr);
    } else {
        tr = $('Table_'+feat.id);
        tr.innerHTML = '';
    }
    pushTD( tr, feat.gcpId ? feat.gcpId : "--", 'Id_'+featuresArray.indexOf(feat)  );
    pushTD( tr, pt.lon.toFixed(6) );
    pushTD( tr, pt.lat.toFixed(6) );
    pushTD( tr, feat.lonlat.lon.toFixed(2) );
    pushTD( tr, (userMap.maxExtent.top - feat.lonlat.lat).toFixed(2) );
    pushTD( tr, "", 'Error_'+featuresArray.indexOf(feat) );
    
}   
function loadFilename(file) {
    filename = file;
    addScript(API_PATH+"/info/"+filename+"?handler=loadGcpsHandler", "Loading data...");
} 
function loadGcpsHandler(data) {
    var mouseDefaults = new OpenLayers.Control.MouseDefaults();
    mouseDefaults.defaultDblClick = function () { return true; };

    userMap = new OpenLayers.Map('userMap',
        { controls: [mouseDefaults, new OpenLayers.Control.PanZoomBar()],
          maxExtent: new OpenLayers.Bounds(0,0,data.width,data.height),
          maxResolution: 'auto',
          numZoomLevels: 8});
    var wms = new OpenLayers.Layer.WMS.Untiled( "User Map WMS", 
        WMS_PATH, {layers: 'image', 'image': data.filename} )  ;
    markers = new OpenLayers.Layer.Markers("Markers");
    userMap.addLayers([wms, markers]);
    userMap.zoomToMaxExtent();

    userMap.events.register("dblclick", userMap, addGCP);
    if (data.gcps.length) {
        var gcp0 = data.gcps[0];
        var refBounds = new OpenLayers.Bounds(gcp0[0],gcp0[1],gcp0[0],gcp0[1]);
        for(var i=0; i<data.gcps.length; i++) {
            var id = createGcp(new OpenLayers.LonLat(data.gcps[i][2], data.height - data.gcps[i][3]));
            gcpBeingEdited = id;
            modifyGCP(new OpenLayers.LonLat(data.gcps[i][0], data.gcps[i][1]));
            if (data.gcps[i][0] < refBounds.left) { refBounds.left = data.gcps[i][0]; } 
            if (data.gcps[i][0] > refBounds.right) { refBounds.right = data.gcps[i][0]; } 
            if (data.gcps[i][1] > refBounds.top) { refBounds.top = data.gcps[i][1]; } 
            if (data.gcps[i][1] < refBounds.bottom) { refBounds.bottom = data.gcps[i][1]; } 
        }
        refMap.zoomToExtent(refBounds);
    }
    gcpBeingEdited = null;
    if (data.warped)
        addWarpedWMSLayer(data.warped);
    updateData(data);
}    
function addWarpedWMSLayer (imagename) {
    warpedWMSLayer = new OpenLayers.Layer.WMS.Untiled( "User Map WMS (Warped)", 
        WMS_PATH, {layers: 'image', 'image': imagename, format:'image/png', TRANSPARENT:'true'} );
    refMap.addLayer(warpedWMSLayer);
    warpedWMSLayer.setOpacity(.7);
}
function addScript(url, status) {
    $('status').innerHTML = status;
    var s = document.createElement("script");
    s.src=url;
    document.getElementsByTagName("head")[0].appendChild(s);
}    
    
function removeLocation(id) {
    markers.removeMarker(features[id].marker);
    if (features[id].data.refMarker) {
        refMarkers.removeMarker(features[id].data.refMarker);
    }    
    userMap.removePopup(features[id].popup);
    if ($('Table_'+id)) {
        var table = $('gcpTable');
        table.removeChild($('Table_'+id));
    }
    featuresArray.remove(features[id]);
    if (features[id].gcpId) {
        addScript(API_PATH+"/delete/"+filename+"?" +
            "gcp="+features[id].gcpId+"&handler=updateData", "Removing GCP "+features[id].gcpId);
    }        
    delete features[id];
    return false;
}    

function toggleLocationPopup (evt, id) {
    var popup;
    if (id != null) {
        popup = features[id].popup;
    } else {
        popup = this.popup;
        id    = this.id;
    }
    if (popup.visible()) {
        popup.hide();
        setCurrentGCP(null);
        if ($('Table_'+id)) $('Table_'+id).style.backgroundColor='';
    } else {
        for (var i in features) 
            if (typeof features[i] != 'function') {
                if ($('Table_'+i)) $('Table_'+i).style.backgroundColor='';
                features[i].popup.hide();
            }    
        if (!features[id].onScreen()) {
            userMap.setCenter(features[id].lonlat);
        }    
        popup.show();
        $(id + '_Input').focus();
        setCurrentGCP(id);
        if ($('Table_'+id)) { $('Table_'+id).style.backgroundColor='lightyellow'; }
    }
    Event.stop(evt);
    return false;
}   

function startRectify() { 
    OpenLayers.Util.onImageLoadError = function() {  this.style.display = ""; this.src="http://labs.metacarta.com/wms-c/nodata.png"; }
 
    var mouseDefaults = new OpenLayers.Control.MouseDefaults();
    
    mouseDefaults.defaultDblClick = function () { return true; };
    refMap = new OpenLayers.Map('refMap',
        { numZoomLevels: 18, maxResolution: 1.40625/2,
          controls: [mouseDefaults, new OpenLayers.Control.PanZoomBar(),
                     new OpenLayers.Control.LayerSwitcher()]}
    );
    var wms2 = new OpenLayers.Layer.WMS( "OpenLayers WMS", 
        "http://labs.metacarta.com/wms-c/Basic.py?", {layers: 'basic'} 
    );
    var googlesat = new OpenLayers.Layer.Google("Google Satellite", {'type':G_SATELLITE_MAP, 'maxZoomLevel':18}); 
    var jpl_wms = new OpenLayers.Layer.KaMap( "Satellite",
       "http://openlayers.org/world/index.php", {g: "satellite", map: "world"});

    refMarkers = new OpenLayers.Layer.Markers("Markers");
    refMap.addLayers([wms2,jpl_wms, googlesat, refMarkers]);
    refMap.zoomToMaxExtent();
    refMap.events.register("dblclick", refMap, modifyGCPEvent);
    var path = document.location.pathname.split("/");
    var filename = path[path.length-1];
    loadFilename(filename);
}

function startWarp() {
    var warpType = $('warpType')
    var order = warpType.options[warpType.selectedIndex].value;
    addScript(API_PATH+"/warp/"+filename+"?order="+order+"&handler=updateData", 
              "Warping image... Please be patient!" );
}    
