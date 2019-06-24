const twit = require('twit');
const Promise = require('bluebird');
const fs = require('fs');
const assert = require('assert');
const rp = require('request-promise');
const request = require('request');
const Queue = require('bull');
const config = require('./config');
const twitter = new twit(config.twitter);
const tweetQueue = new Queue('retweet', config.redis);
const redditQueue = new Queue('reddit', config.redis);
const nineGagQueue = new Queue('9gag', config.redis);
const _ = require('lodash');

// var matador = require('bull-ui/app')({
//   redis: config.redis
// });
// matador.listen(1337, function () {
//   console.log('bull-ui started listening on port', this.address().port);
// });

const twitterWorker = require('./worker/upload-tweet')(twitter, tweetQueue)
const redditWorker = require('./worker/reddit-fetcher')(redditQueue, tweetQueue)
const nineGagWorker = require('./worker/nine-gag-fetcher')(nineGagQueue, tweetQueue)

const repeatPramas = {
  repeat: {
    cron: '*/30 * * * *'
  }
}
nineGagQueue.on('error', function (err) {
  console.log('error', err)
})
nineGagQueue.add({
  'url': 'http://9gag-rss.com/api/rss/get?code=9GAG&format=1'
}, repeatPramas);

redditQueue.add({
  'url': 'https://www.reddit.com/r/funny.json'
}, {
  repeat: {
    cron: '6 */1 * * *'
  }
});


var stream = twitter.stream('user');  


stream.on('follow', function (stream_event) {  
    console.log('Someone just followed us');
    var user_name = stream_event.source.screen_name;
    var tweet = {
        status: '@' + user_name + ' Nice to meet you.'
    }

    twitter.post('statuses/update', tweet, function(err, data, response) {
      if(err){
        console.log("Error tweeting");
      }
      else{
        console.log("tweeted successfully");
      }
    });
});  
