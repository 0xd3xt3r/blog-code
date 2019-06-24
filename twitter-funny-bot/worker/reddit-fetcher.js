
const request = require('request')
const _ = require('lodash');

module.exports = function (redditQueue, tweetQueue) {
  console.log('Reddit worker initialized')
  redditQueue.process((job, done) => {
    console.log('processing reddit')
    const redditUrl = job.data.url;
    request.get({
      method: 'GET',
      url: redditUrl,
      json: true
    }, (err, body, data) => {
      if(data){
        _.each(data.data.children, (post) => {
          let content = {
            url: post.data.url,
            title: post.data.title
          }
          tweetQueue.add(content)
        });
      }
      done();
    })
  })
}
