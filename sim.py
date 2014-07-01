import datetime, sched, time, city, road, house, sys, random, urllib2, occupent, pymongo
from pymongo import MongoClient

# variable for db
db, client, events, houses = None, None, None, None

# variable for simulation
sim_count = 0 #pc
sim_speed = 1 #seconds

# variable for city creation
num_roads = 50 
prob_intersect = 0 #TODO 
city_nw = (42.380104,-72.536373)
city_ne = (42.380104,-72.511997)
city_sw = (42.367931,-72.536373)
city_se = (42.367931,-72.51197)

# variables for road creation
num_houses_upper_bound = 30
num_houses_lower_bound = 1
prob_road_outage_upper_bound = 50 #changed
prob_road_horizontal = 50
prob_add = 50
road_lat_delta_upper_bound = 0.04 
road_lat_delta_lower_bound = 0.005
road_lng_delta_upper_bound = 0.04
road_lng_delta_lower_bound = 0.005
road_horizontal_type = 1

# variables for house creation
max_occupents = 4
prob_house_outage_upper_bound = 10
house_lat_delta_upper_bound = 0.003
house_lat_delta_lower_bound = 0.0009
house_lng_delta_upper_bound = 0.002
house_lng_delta_lower_bound = 0.0009

# variables for occupent creation
prob_gw_owner_upper_bound = 40
prob_phone_plugged_in_upper_bound = 70
prob_false_positive_upper_bound = 10
prob_gw_retention_upper_bound = 90

def create_occupents(num_occupents):
  global prob_gw_owner_upper_bound, prob_phone_plugged_in_upper_bound, prob_false_positive_upper_bound, prob_gw_retention_upper_bound
  occupent_list = []
  for new_occupent in range(0, num_occupents):
    cur_occupent = occupent.Occupent( 
           phone_plugged_in_percent=cur_probability(prob_phone_plugged_in_upper_bound), 
           false_positive_percent=cur_probability(prob_false_positive_upper_bound), 
           gw_retention_percent=cur_probability(prob_gw_retention_upper_bound), 
           gw_owner=cur_probability(prob_gw_owner_upper_bound)
    )
    occupent_list.append(cur_occupent)
  return occupent_list

def get_house_spacing(road_start_point, road_end_point, num_houses):
  #TODO currently we are ignoring reasonable spacing from a max delta...
  if (road_start_point[0] == road_end_point[0]): #lats a equal, road runs lng
     distance = abs(road_start_point[1] - road_end_point[1])
  else:
     distance = abs(road_start_point[0] - road_end_point[0])
  spacing = distance / num_houses

  #print "house spacing on road is: " + str(spacing)
  
  new_num_houses = num_houses
  while 1: # to prevent over crowded roads
    if (new_num_houses == 1):
      break
    if (spacing < 0.002):
      print "spacing: " + str(spacing)
      print "new_num_houses: " + str(new_num_houses) 
      new_num_houses = new_num_houses - 1
      spacing = distance / new_num_houses
    else:
      break
  return (spacing, new_num_houses)

def get_house_lat_lng(road_start_point, road_end_point, house_num, spacing, road_type):
  #TODO make sure house is in road box
  current_space = house_num * spacing  

  if (road_type == road_horizontal_type):
    # adding delta to lng
    house_lat = road_start_point[0]
    if (road_start_point[1] < road_end_point[1]):
      house_lng = road_start_point[1] + current_space
    else:
      house_lng = road_start_point[1] - current_space
  else:  
    # adding delta to lat
    house_lng = road_start_point[1]
    if (road_start_point[0] < road_end_point[0]):
      house_lat = road_start_point[0] + current_space
    else:
      house_lat = road_start_point[0] - current_space

  #print str(house_lat) + "," + str(house_lng)
  return (house_lat, house_lng)

def create_houses(num_houses, road_start_point, road_end_point, road_type, road_num): #TODO just take a road
  global max_occupents, prob_house_outage_upper_bound, houses
  house_list = []
  house_num = 0
  spacing, new_house_num = get_house_spacing(road_start_point, road_end_point, num_houses)

  for new_house in range(0, new_house_num):
     num_occupents = random.randint(1, max_occupents)
     occupentlist = create_occupents(num_occupents)
     house_lat, house_lng = get_house_lat_lng(road_start_point, road_end_point, house_num, spacing, road_type)
     house_num_str = "R"+str(road_num)+"H"+str(house_num)
     cur_house = house.House(
           lat=house_lat,
           lng=house_lng,
           num=house_num_str,
           random_outage_percent=cur_probability(prob_house_outage_upper_bound), 
           occupent_list=occupentlist
     ) 
     
     db_house = {"time" : gen_time(10),
        "num": house_num_str,
        "lat": house_lat,
        "lng": house_lng,
        "outage_cnt": 0}
     print "        inserting " + str(db_house)
     houses.insert(db_house)
   
     house_list.append(cur_house)
     house_num = house_num + 1
  return house_list

def check_city_bounds(point, delta, type): #TODO this is broken... fix when can look up
  return 1
  global city_nw, city_ne, city_sw, city_se 
  print "checking city bound"
  print " delta = " + str(delta)
  if (type == 0): #lat
     print " min = " + str(point-delta)
     if (point+delta > city_nw[0]): 
       print str(point+delta) + " > lat city n: " + str(city_nw[0])
       return 0
     if (point-delta < city_se[0]): 
       print str(point-delta) + " < lat city s: " + str(city_se[0])
       return 0
     return 1
  else:
     if (point+delta > city_nw[1]): 
       print str(point+delta) + " > lng city w: " + str(city_nw[1]) 
       return 0
     if (point-delta < city_se[1]): 
       print str(point-delta) + " <  lng city e: " + str(city_se[1]) 
       return 0
     return 1
  return 0 

def get_road_lat_lng(city_nw, city_ne, city_sw, city_se, road_horizontal):
  global road_horizontal_type  

  vertical_upper = city_nw[0]
  vertical_lower = city_sw[0]
  horizontal_upper = city_nw[1]
  horizontal_lower = city_ne[1]

  start_lat = play_float(vertical_lower, vertical_upper)
  start_lng = play_float(horizontal_lower, horizontal_upper)
  start_point = (start_lat, start_lng)
  
  if (road_horizontal == road_horizontal_type):
    #print "road horizontal!"
    #adding delta to lng
    end_lat = start_lat
    while (1): 
      road_lng_delta = play_float(road_lng_delta_lower_bound, road_lng_delta_upper_bound) 
      if (check_city_bounds(start_lng, road_lng_delta, type=1) == 1):
        if (play_probability(prob_add) == 1): #random direction from starting point
          end_lng = play_float(start_lng, start_lng+road_lng_delta)
        else:
          end_lng = play_float(start_lng, start_lng-road_lng_delta)
        break
  else: 
    #print "road vertical!"
    #adding delta to lat
    end_lng = start_lng #we are making boxes...
    while (1):
      road_lat_delta = play_float(road_lat_delta_lower_bound, road_lat_delta_upper_bound) 
      if (check_city_bounds(start_lat, road_lat_delta, type=0) == 1):
        if (play_probability(prob_add) == 1): #random direction from starting point
          end_lat = play_float(start_lat, start_lat+road_lat_delta)
        else:   
          end_lat = play_float(start_lat, start_lat-road_lat_delta)
        break

  end_point = (end_lat, end_lng) 
  #print "road start lat/lng: " + str(start_point) 
  #print "road end lat/lng: " + str(end_point)
  return (start_point, end_point)

def create_roads(num_roads, min_houses, max_houses):
  global prob_road_outage_upper_bound, city_nw, city_ne, city_sw, city_se
  road_list = []
  road_cnt = 0
  for new_road in range(0, num_roads):
     num_houses = random.randint(min_houses, max_houses)
     road_type = play_probability(prob_road_horizontal)
     road_start_point, road_end_point = get_road_lat_lng(city_nw, city_ne, city_sw, city_se, road_type)
     houselist = create_houses(num_houses, road_start_point, road_end_point, road_type, road_cnt)
     cur_road = road.Road(
          num=road_cnt, 
          start_point = road_start_point,
          end_point = road_end_point,
          percent_out=cur_probability(prob_road_outage_upper_bound),
          houselist=houselist
     ) 
     road_list.append(cur_road)
     road_cnt = road_cnt + 1
  return road_list

def create_city():
  print "new city!"
  global num_roads, num_houses_lower_bound, num_houses_upper_bound
  roadlist = create_roads(
      num_roads=num_roads, 
      min_houses=num_houses_lower_bound, 
      max_houses=num_houses_upper_bound,
  )
  the_city = city.City(
      box_n=city_nw,
      box_e=city_ne,
      box_w=city_sw,
      box_s=city_se,
      roadlist=roadlist
  )
  return the_city  

def play_float(lower_bound, upper_bound):
  return random.uniform(lower_bound, upper_bound) 

def cur_probability(upper_bound): #TODO
  return random.randint(1, upper_bound)

def play_probability(range):  
  hit = random.randint(0, 99)
  if (hit < range): return 0
  else: return 1

def print_occupent(occupent):
   print "         false_positive_percent: " + str(occupent.false_positive_percent)
   print "         plugged in percent: " + str(occupent.phone_plugged_in_percent)
   print "         gw_owner: " + str(occupent.gw_owner)  
   print "         gw_retention_percent: " + str(occupent.gw_retention_percent)  

def print_house(house):
  print "    House probabilities this run:"
  print "      house num: " + str(house.num)
  print "      occupents: " + str(len(house.occupentlist))
  #occupent_cnt = 0;
  #for occupent in house.occupentlist:
   #print "       occupent num: " + str(occupent_cnt)
   #print_occupent(occupent)
   #occupent_cnt = occupent_cnt + 1

def initalize_db():
  global client, db, events, houses
  client = MongoClient()
  db = client.packet_db
  events = db.events
  houses = db.houses
  if (1 == 1): #TODO add cmd line argument
    events.remove()
    houses.remove()

def mod_secs(tm, secs):
  fulldate = datetime.datetime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second)
  if (get_switch() == 1):
    fulldate = fulldate + datetime.timedelta(seconds=secs)
  else:
    fulldate = fulldate - datetime.timedelta(seconds=secs)
  return fulldate

def get_switch():
  return random.randint(0,1)

def gen_time(range):
  offset = random.randint(0, range)
  return mod_secs(datetime.datetime.today(), offset)

def report_outage(house, occupant_num):
  global events
  print "        ############ OUTAGE from " + str(occupant_num) + " ######## " 
  event = {"time": gen_time(100),
        "num": house.num,
        "lat": house.lat,
        "lng": house.lng,
        "occupant": occupant_num}
  print "        inserting " + str(event)
  return events.insert(event) 
  

def update_house(house, road_state):
  print_house(house)
  print "      House actions this run:"

  # Each occupent can either report a true or false positive or nothing at all... 
  # we first give them a chance to report a false positive... this removes them from any other reports
  non_reported_occupents = []
  occupent_cnt = 0
  for occupent in house.occupentlist:
      if (play_probability(occupent.false_positive_percent) == 0): # give each occupent a chance to cause a false positive
           print "        FALSE POSITIVE by occupent " + str(occupent_cnt) 
           report_outage(house, occupent_cnt) #TODO think about whether this makes sense 
      else:     
           non_reported_occupents.append(occupent)           
      occupent_cnt = occupent_cnt + 1

  if (road_state == 0 or play_probability(house.random_outage_percent) == 0): # you have a random house outage or road outage... 
      if (road_state == 0):
         print "         road outage!" 
      else:
         print "         random house outage!"
      
      occupent_cnt = 0
      for occupent in non_reported_occupents: # did any occupent that has not already reported catch it?
        print "          processing occupent " + str(occupent_cnt)
        if (occupent.gw_owner == 1): # if an occupent owns grid watch...
          print "              gw owner!" 
          if (play_probability(occupent.phone_plugged_in_percent) == 0): # if an occupent's phone is plugged in...
             print "              plugged in!"
             report_outage(house, occupent_cnt) #TODO add false negatives
          else:
             print "              not plugged in!"
          if (play_probability(occupent.gw_retention_percent) == 1):
             print "              gw retained!" 
             occupent.gw_owner = 1
          else: 
             occupent.gw_owner = 0  
        else: 
          print "              not gw owner!"
        occupent_cnt = occupent_cnt + 1
  else:
      print "        no outage" 

def run(sc, city):
  global sim_count, sim_speed
  print "###############################################" 
  print "# SIM COUNT: " + str(sim_count)
  print "###############################################" 
  for road in city.roadlist:
    print "Road probabilities this run: " 
    print "  road num: " + str(road.num)
    print "  road outage probability: " + str(road.percent_out)
    if (play_probability(road.percent_out) == 0): #the road is out
      print "  road outage!"
      for house in road.houselist:
        update_house(house=house, road_state=0)
    else: 
      print "  no road outage!"
      for house in road.houselist:
        update_house(house=house, road_state=1)
  sim_count = sim_count + 1
  sc.enter(sim_speed,1,run,(sc,city))

def main(argv):
  global sim_speed
  initalize_db()
  city = create_city()
  s = sched.scheduler(time.time, time.sleep)
  s.enter(sim_speed,1,run,(s,city))
  s.run()

if __name__ == "__main__":
  main(sys.argv[1:])
