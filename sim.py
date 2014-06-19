import datetime, sched, time, city, road, house, sys, random, urllib2, occupent, pymongo
from pymongo import MongoClient

# variable for db
db, client, events = None, None, None

# variable for simulation
sim_count = 0
sim_speed = 1

# variable for city creation
num_roads = 2

# variables for road creation
num_houses_upper_bound = 10
num_houses_lower_bound = 1
prob_road_outage_upper_bound = 50

# variables for house creation
max_occupents = 4
prob_house_outage_upper_bound = 10

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
 
def create_houses(num_houses):
  global max_occupents, prob_house_outage_upper_bound
  house_list = []
  house_num = 0
  for new_house in range(0, num_houses):
     num_occupents = random.randint(1, max_occupents)
     occupentlist = create_occupents(num_occupents)
     cur_house = house.House(
           lat=1,
           lng=2,
           num=house_num,
           random_outage_percent=cur_probability(prob_house_outage_upper_bound), 
           occupent_list=occupentlist
     ) 
     house_list.append(cur_house)
     house_num = house_num + 1
  return house_list

def create_roads(num_roads, min_houses, max_houses):
  global prob_road_outage_upper_bound
  road_list = []
  road_cnt = 0
  for new_road in range(0, num_roads):
     num_houses = random.randint(min_houses, max_houses)
     houselist = create_houses(num_houses)
     cur_road = road.Road(
          num=road_cnt, 
          box_n=1,
          box_e=2,
          box_w=3,
          box_s=4,
          percent_out=cur_probability(prob_road_outage_upper_bound),
          houselist=houselist
     ) 
     road_list.append(cur_road)
     road_cnt = road_cnt + 1
  return road_list

def create_city():
  print "new city!"
  global num_roads, num_houses_lower_bound, num_houses_upper_bound
  roadlist = create_roads(num_roads=num_roads, min_houses=num_houses_lower_bound, max_houses=num_houses_upper_bound)
  the_city = city.City(box_n=10,box_e=20,box_w=30,box_s=40,roadlist=roadlist)
  return the_city  

def cur_probability(upper_bound): #TODO
  range = random.randint(1, upper_bound)
  return range

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
  global client, db, events
  client = MongoClient()
  db = client.packet_db
  events = db.events
  if (1 == 1): #TODO add cmd line argument
    events.remove()

def mod_secs(tm, secs):
  fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
  if (get_switch() == 1):
    fulldate = fulldate + datetime.timedelta(seconds=secs)
  else:
    fulldate = fulldate - datetime.timedelta(seconds=secs)
  return fulldate

def get_switch():
  return random.randint(0,1)

def gen_time(range):
  offset = random.randint(0, range)
  return mod_secs(datetime.datetime.now().time(), offset)

def report_outage(house, occupant_num):
  global events
  print "              ############ OUTAGE ######## " 
  event = {"time": gen_time(100),
        "lat": house.lat,
        "lng": house.lng,
        "occupant": occupant_num}
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
        else: 
          print "              not gw owner!"
        if (play_probability(occupent.gw_retention_percent) == 1):
          print "              gw retained!" 
          occupent.gw_owner = 1
        else: 
          occupent.gw_owner = 0  
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
  city = create_city()
  initalize_db()
  s = sched.scheduler(time.time, time.sleep)
  s.enter(sim_speed,1,run,(s,city))
  s.run()

if __name__ == "__main__":
  main(sys.argv[1:])
