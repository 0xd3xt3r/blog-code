const uploadRemoteMedia = require('../utils').uploadRemoteMedia;
const sw = require('stopword')
const _ = require('lodash');

module.exports = function (twitter, tweetQueue) {
  console.log('Twitter worker initialized')
  tweetQueue.process(function (job, done) {
    const content = job.data;
    console.log('processing', content)
    uploadRemoteMedia(twitter, content.url)
      .then((bodyObj) => {
        const newString = sw.removeStopwords(content.title.split(' '))
        if (newString.length > 0) {
          let already = {};
          for (let i = 0; i < 3; i++) {
            let replace_word = newString[_.random(0, newString.length)]
            if (!already[replace_word]) {
              content.title = content.title.replace(replace_word, '#' + replace_word)
            }
            already[replace_word] = true;
          }
        }
        let status = {
          status: content.title,
          media_ids: bodyObj.media_id_string // Pass the media id string
        };
        twitter.post('statuses/update', status, function (error, tweet, response) {
          if (error) {
            console.log('tweeting error');
          } else {
            console.log('tweeted');
          }
          done();
        });
      })
      .catch((err) => {
        console.log('upload err', err);
        done();
      })
  })
}
