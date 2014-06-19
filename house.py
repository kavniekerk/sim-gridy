class House:

  def __init__(self, lat, lng, num, random_outage_percent, occupent_list):
    self.lat = lat
    self.lng = lng
    self.num = num
    self.occupentlist = occupent_list
    #self.phone_plugged_in_percent = phone_plugged_in_percent
    #self.false_positive_percent = false_positive_percent
    #self.gw_retention_percent = gw_retention_percent
    self.random_outage_percent = random_outage_percent
    #self.gw_owner = gw_owner
