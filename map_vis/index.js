var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var mongoose = require('mongoose');
var pc = 0

io.on('connection', function(socket){
  console.log('a user connected');
});

function find (collec, query, callback) {
    mongoose.connection.db.collection(collec, function (err, collection) {
    collection.find(query).toArray(callback);
    });
}

mongoose.connect('mongodb://localhost/packet_db');
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function callback() {
  console.log('db connected');
});

function blob_houses() {
 console.log(pc);
 find('final_db', {}, function (err, docs) {
    if (typeof docs[0] !== 'undefined') {
      io.emit('msg', docs[0].msg); // send out the blob from the server on
    } else {
      console.log("packet dropped")  
    };
 }); 
 pc += 1
}

setInterval(function() {
 blob_houses()
}, 1000);

app.get('/', function(req, res){
  res.sendfile('index.html');
});

app.get('/outage.png', function(req, res){
  res.sendfile('outage.png');
});

app.get('/power.png', function(req, res){
  res.sendfile('power.png');
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
