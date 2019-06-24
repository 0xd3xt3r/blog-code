const FeedParser = require('feedparser');
const request = require('request');
const feedparser = new FeedParser();
const cheerio = require('cheerio');


module.exports = function (nineGagQueue, tweetQueue) {
  console.log('9Gag worker initialized')
  nineGagQueue.process((job, done) => {
    const gagFeedUrl = job.data.url;
    const req = request(gagFeedUrl)

    req.on('error', function (error) {
      console.log('Feed fetching', error)
    });

    req.on('response', function (res) {
      let stream = this;

      if (res.statusCode !== 200) {
        this.emit('error', new Error('Bad status code'));
      } else {
        stream.pipe(feedparser);
      }
    });

    feedparser.on('error', function (error) {
      console.log('Feed Error', error)
    });

    feedparser.on('readable', function () {
      let stream = this;
      let item, content = {};

      while (item = stream.read()) {
        console.log('Reading feed');
        content.title = cheerio.load(item.title).text();
        $ = cheerio.load(item.description);
        links = $('img');
        if ($(links).length != 0) {
          if ($(links).length != 0) {
            $(links).each(function (i, link) {
              content.url = $(link).attr('src');
            });
          }
        } else {
          links = $('source');
          if ($(links).length != 0) {
            $(links).each(function (i, link) {
              content.url = $(link).attr('src');
            });
          }
        }
        tweetQueue.add(content);
      }
      setTimeout(() => {
          done()
        },
        1000 * 60 * 15)
    });
  })
}
