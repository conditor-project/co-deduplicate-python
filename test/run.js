/* eslint-disable no-unused-expressions */
/* eslint-disable no-undef */

const chai = require('chai');
const _ = require('lodash');
const expected = require('./dataset/expected');
const business = require('../index.js');

const { expect } = chai;

describe('index.js', () => {
  const data = require('./dataset/in/goodDocObjects.json');

  describe('#beforeAnyJob', () => {
    it('Python and Pip are installed on the system.', (done) => {
      business.beforeAnyJob((err) => {
        expect(err).to.be.undefined;
        done();
      });
    });
  });

  describe('#doTheJob', () => {
    it('testData.correct is correct.', (done) => {
      const correctData = _.cloneDeep(data[0]);
      business.doTheJob(correctData, (err) => {
        expect(correctData.duplicates).to.include.deep.members([expected.correct]);
        expect(correctData.errCode).to.be.undefined;
        expect(err).to.be.undefined;
        done();
      });
    });
  });
});
