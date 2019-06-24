const request = require('request');

module.exports.uploadRemoteMedia = function (twitter, content_url) {
  return new Promise((resolve, reject) => {
    const remoteFileStream = request(content_url);
    let mediaIdStr;
    let _finalizeMedia = function (mediaIdStr, cb) {
      twitter.post('media/upload', {
        'command': 'FINALIZE',
        'media_id': mediaIdStr
      }, cb)
    }

    let _checkFinalizeResp = function (err, bodyObj, resp) {
      if (err) reject(new Error(err))
      else {
        resolve(bodyObj)
      }
    }

    let isStreamingFile = true;
    let isUploading = false;
    let segmentIndex = 0;
    remoteFileStream.on('response', function (res) {
      process.stdout.write('Uploading started...');
      remoteFileStream.pause();
      twitter.post('media/upload', {
        'command': 'INIT',
        'media_type': res.headers['content-type'],
        'total_bytes': res.headers['content-length']
      }, function (err, bodyObj, resp) {
        remoteFileStream.resume();
        if (err) reject(new Error(err))
        mediaIdStr = bodyObj.media_id_string;
      });
    });

    remoteFileStream.on('data', function (buff) {
      process.stdout.write('.');
      remoteFileStream.pause();
      // isStreamingFile = false;
      isUploading = true;
      twitter.post('media/upload', {
        'command': 'APPEND',
        'media_id': mediaIdStr,
        'segment_index': segmentIndex,
        'media': buff.toString('base64'),
      }, function (err, bodyObj, resp) {
        if (err) reject(new Error(err))
        segmentIndex++;
        isUploading = false;

        if (!isStreamingFile) {
          _finalizeMedia(mediaIdStr, _checkFinalizeResp);
        }
        remoteFileStream.resume();
      });
    });

    remoteFileStream.on('end', function () {
      console.log('done')
      isStreamingFile = false;
      if (!isUploading) {
        _finalizeMedia(mediaIdStr, _checkFinalizeResp);
      }
    });
  })
}
