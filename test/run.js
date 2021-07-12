/* eslint-disable no-unused-expressions */
/* eslint-disable no-undef */

const chai = require('chai');
const _ = require('lodash');
const { errorList } = require('../error.js');
const expected = require('./dataset/expected');
const business = require('../index.js');
const { getConfigPath } = require('../config/configGetter');

const { expect } = chai;

describe('index.js', () => {
  const data = require('./dataset/in/goodDocObjects.json');

  data.forEach((docObject) => {
    business.doTheJob(docObject, (err) => {
      if (err) console.error(err);
    });
  });

  describe('#finalJob', () => {
    it('testData.correct is correct', (done) => {
      const correctData = _.cloneDeep(data);
      business.config = require(getConfigPath()).get();
      business.finalJob(correctData, (err) => {
        expect(correctData[0].duplicates).to.include.deep.members([expected.correct]);
        expect(correctData[0].errCode).to.be.undefined;
        expect(err).to.be.undefined;
        done();
      });
    });

    it('testData.httpError generates an HTTP error', (done) => {
      const httpErrorData = _.cloneDeep(data);
      business.config.uri = 'error'; // Injects an error into the config
      business.finalJob(httpErrorData, (err) => {
        expect(httpErrorData[0].errCode).to.be.not.undefined;
        expect(err).to.be.not.undefined;
        expect(err.name).to.be.equal(errorList.HttpError);
        done();
      });
    });

    it('testData.networkError generates a network error', (done) => {
      const networkErrorData = _.cloneDeep(data);
      business.config.host = 'bad.address'; // Injects an error into the config
      business.finalJob(networkErrorData, (err) => {
        expect(networkErrorData[0].errCode).to.be.not.undefined;
        expect(err).to.be.not.undefined;
        expect(err.name).to.be.equal(errorList.NetworkError);
        done();
      });
    });
  });
});
