const request = require('request');
const async = require('async');
const { getConfigPath, buildServiceURL } = require('./config/configGetter');
const { errorList, handleError } = require('./error.js');

const business = {};
business.config = require(getConfigPath()).get();

business.doTheJob = (docObject, callback) => {
  return callback();
};

business.finalJob = (docObjects, callback) => {
  const body = [];

  for (let i = 0; i < docObjects.length; i++) {
    body.push({
      id: i,
      value: docObjects[i],
    });
  }

  async.retry(business.config.retry, (retryCallback) => sendRequest(body, retryCallback), (err, result) => {
    let finalError;

    for (let i = 0; i < docObjects.length; i++) {
      if (err) {
        finalError = handleError(docObjects[i], errorList.NetworkError);
        continue;
      }

      if (result.response.statusCode.toString()[0] !== '2') {
        const error = new Error(`Service co-duplicates (${business.config.url}) responding with status code: ${result.response.statusCode}`);
        error.code = result.response.statusCode;
        finalError = handleError(docObjects[i], errorList.HttpError, error);
        continue;
      }

      const response = JSON.parse(result.body.toString());
      response[i].value.duplicates.forEach((duplicate) => {
        const found = docObjects[i].duplicates.find((dupInDocObject) => dupInDocObject.sourceUid === duplicate.sourceUid);
        if (!found) docObjects[i].duplicates.push(duplicate);
      });
    }

    docObjects = [];
    return callback(finalError);
  });
};

/**
 * Sends a request to the web service.
 * @param {object} formData The data to send to the web service.
 * @param {function} callback The callback.
 */
function sendRequest (body, callback) {
  const params = {
    method: 'POST',
    url: buildServiceURL(business.config),
    body: Buffer.from(JSON.stringify(body)),
    encoding: null,
  };

  request(params, (err, response, body) => {
    return callback(err, {
      response,
      body,
    });
  });
}

module.exports = business;
