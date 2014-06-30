import city, road, house, occupent

map_name = "map"
zoom = 4

def build_js_start(center):
  global map_name, zoom
  init_str = "function initialize() {\n"
  init_str += "\tvar centerLatlng = new google.maps.LatLng("+str(center[0])+","+str(center[1])+");\n"
  init_str += "\tvar mapOptions = {\n"
  init_str += "\t\tzoom: "+str(zoom)+",\n"
  init_str += "\t\tcenter: centerLatlng\n"
  init_str += "\t};\n"
  init_str += "\tvar " + map_name + " = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);"
  return init_str

def build_road_line(road_start_lat_lng, road_end_lat_lng, road_num):
   global map_name
   road_str = "\tvar road" + str(road_num) + " = [ \n"
   road_str += "\t\tnew google.maps.LatLng(" + str(road_start_lat_lng[0]) + "," + str(road_start_lat_lng[1]) + "),\n" 
   road_str += "\t\tnew google.maps.LatLng(" + str(road_end_lat_lng[0]) + "," + str(road_end_lat_lng[1]) + ")\n\t];\n\n" 
   road_str += "\tvar road" + str(road_num) + "Path = new google.maps.Polyline({\n"
   road_str += "\t\tpath: road" + str(road_num) + ",\n"
   road_str += "\t\tgeodesic: true,\n"
   road_str += "\t\tstrokeColor: '#FF0000',\n"
   road_str += "\t\tstrokeOpacity: 1.0,\n"
   road_str += "\t\tstrokeWeight: 2\n\t});\n" 
   road_str += "\troad" + str(road_num) + ".setMap(" + map_name + ");\n"
   return road_str

def build_house_info(house):
   info_str = '''\tvar contentString''' + str(house.num) + ''' = '<div id="content">'+\n'''
   info_str += '''\t\t'<div id="siteNotice">'+\n'''
   info_str += "\t\t'</div>'+\n"
   info_str += '''\t\t'<h1 id="firstHeading" class="firstHeading">Uluru</h1>'+\n'''
   info_str += '''\t\t'<div id="bodyContent">'+\n'''
   info_str += "\t\t'<p><b>House Num " + str(house.num) + "</b> ' +\n"
   info_str += "\t\t'Lat: 335&#160;km '+\n"
   info_str += "\t\t'Lng: 450&#160;km '+\n"
   info_str += "\t\t'(last visited June 22, 2009).</p>'+\n"
   info_str += "\t\t'</div>'+\n"
   info_str += "\t\t'</div>';\n\n"

   info_str += "\tvar infowindow" + str(house.num) + " = new google.maps.InfoWindow({\n"
   info_str += "\t\tcontent: contentString" + str(house.num) + ",\n"
   info_str += "\t\tmaxWidth: 200\n"
   info_str += "\t});"
   return info_str
    
def build_house_marker(house):
  global map_name
  house_lat_lng = str(house.num) + "HouseLatlng"
  marker_str = "\tvar " + house_lat_lng + " = new google.maps.LatLng("+str(house.lat)+","+str(house.lng)+");\n\n"
  marker_str += "\tvar " + house_lat_lng + "Marker = new google.maps.Marker({\n"
  marker_str += "\t\tposition: " + house_lat_lng +",\n"
  marker_str += "\t\tmap: " + map_name + ",\n"
  marker_str += "\t\ttitle: 'HouseNum" + str(house.num) + "'\n"
  marker_str += "\t});\n"
  marker_str += "\tgoogle.maps.event.addListener(" + house_lat_lng +", 'click', function() {\n"
  marker_str += "\t\t infowindow.open(" + map_name + "," + house_lat_lng + ");\n"
  marker_str += "\t});" 
  return marker_str

def build_html_start():
  html_str = "<!DOCTYPE html>\n"
  html_str += "<html>\n"
  html_str += " <head>\n"
  html_str += "    <title>GridSim</title>\n"
  html_str += '''    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">\n'''
  html_str += '''    <meta charset="utf-8">\n'''
  html_str += "    <style>\n"
  html_str += "      html, body, #map-canvas {\n"
  html_str += "        height: 100%;\n"
  html_str += "        margin: 0px;\n"
  html_str += "        padding: 0px\n"
  html_str += "      }\n"
  html_str += "    </style>\n"
  html_str += '''   <script src="https://maps.googleapis.com/maps/api/js?v=3.exp"></script>\n'''
  html_str += "   <script>\n"
  return html_str

def build_html_end():
  html_str = "    </script>\n"
  html_str += "  </head>\n"
  html_str += "  <body>\n"
  html_str += '''    <div id="map-canvas"></div>\n'''
  html_str += "  </body>\n"
  html_str += "</html>\n"
  return html_str

def build_js_end():
  end_js_str = "}\ngoogle.maps.event.addDomListener(window, 'load', initialize);"
  return end_js_str  
 
def build_map(city):
  print "generating JS"

def update_map(house, state):
  print "updating house"

testHouse = house.House(1,2,100,50,[])
road_start_lat_lng = (1,2)
road_end_lat_lng = (3,4)

print build_html_start()
print build_js_start((1,2)) 
#print build_road_line(road_start_lat_lng, road_end_lat_lng, 10)
print build_house_info(testHouse) 
print build_house_marker(testHouse)
print build_js_end()
print build_html_end()
