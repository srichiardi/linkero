


## server daemon
''' receives and queues data requests 
INPUT: routine kwargs + query id + platform id + report type + user id '''

# start report daemon

# connect to mongodb

# listen to client connections

# save query input to queue

# close connection with client

# shut everything down if more than 5 min passed since last report completed


## report daemon
''' executes sequentially all data requests in the queue '''

# retrieve query from queue, check the report type and start the relative routine


## ebay listing process
''' retieves ebay listings data based on seller_id and/or keywords '''

# find items advanced

# get items details

# get seller details


## query threads
''' get data from API and save it in mongo '''