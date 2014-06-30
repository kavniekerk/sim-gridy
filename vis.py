from pymongo import MongoClient
import datetime, sys, sched, time

client, db, events, houses, processed_events  = None, None, None, None, None
vis_update_speed = 1
event_window = 30

def visualize_city():
  global houses
  for house in houses.find():
     print str(house['lat']) + "," + str(house['lng']) 

def process_event(event):
  global events, processed_events
  processed_events.insert(event)
  print str(event['lat']) + "," + str(event['lng'])

def visualize_events():
  #TODO figure out of to restore power to house....
  global events, cur_events
  cur_time = datetime.datetime.today()
  for event in events.find({"time": {"$gte": mod_secs(cur_time, event_window),"$lt": cur_time}}):
     #if event time is in event_windows seconds
     process_event(event)
     events.remove(event)
 
def mod_secs(tm, secs):
  return tm - datetime.timedelta(seconds=secs)

def poll(sc):
  print "update visualization"
  visualize_events() 
  sc.enter(vis_update_speed,1,poll,(sc,))

def initalize_db():
  global client, db, events, processed_events, houses
  client = MongoClient()
  db = client.packet_db
  events = db.events
  houses = db.houses
  processed_events = db.processed_events

def main(argv):
  initalize_db()
  visualize_city()
  s = sched.scheduler(time.time, time.sleep)
  s.enter(vis_update_speed,1,poll,(s,))
  s.run()

if __name__ == "__main__":
  main(sys.argv[1:])

