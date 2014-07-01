from pymongo import MongoClient
import datetime, sys, sched, time, base64

client, db, events, houses, final_db, processed_events  = None, None, None, None, None, None
vis_update_speed = 1
event_window = 5
vis_count = 0

def get_current_events():
  global events, processed_events, houses, final_db
  cur_time = datetime.datetime.today()
  for event in events.find({"time": {"$gte": mod_secs(cur_time, event_window),"$lt": cur_time}}):
    house = houses.find_one({'num': event['num']})
    cur_outage_cnt = house['outage_cnt']
    houses.find_and_modify(query={'num': event['num']}, update={"$set": {'outage_cnt': cur_outage_cnt + 1}}, upsert=False, full_response = True)
    #events.remove(event)

def build_db():
  #TODO figure out of to restore power to house....
  get_current_events()  

def clear_houses():
  global houses
  houses.update({}, {"$set": {'outage_cnt' : 0 }}, multi=True)
 
def visualize_events():
  global final_db, vis_count
  print "update visualization: " + str(vis_count)
  msg = ""
  for house in houses.find():
     datetime = house['time']
     date = datetime.strftime('%y%m%d') #YYMMDD
     time = datetime.strftime('%H%M%S') #HHMMSS
     msg += str("#" + str(house['lat'])[:-3]) + "," + str(house['lng'])[:-3] + "," + str(date) + "," + str(time) + "," + str(house['outage_cnt'])
  print msg
  final_db.remove({})
  blob = {"msg" : base64.b64encode(msg)}
  final_db.insert(blob)
  vis_count += 1 

def mod_secs(tm, secs):
  return tm - datetime.timedelta(seconds=secs)

def poll(sc):
  build_db()
  visualize_events() 
  clear_houses()
  sc.enter(vis_update_speed,1,poll,(sc,))

def initalize_db():
  global client, db, events, final_db, processed_events, houses
  client = MongoClient()
  db = client.packet_db
  events = db.events
  houses = db.houses
  final_db = db.final_db
  processed_events = db.processed_events

def main(argv):
  initalize_db()
  s = sched.scheduler(time.time, time.sleep)
  s.enter(vis_update_speed,1,poll,(s,))
  s.run()

if __name__ == "__main__":
  main(sys.argv[1:])

