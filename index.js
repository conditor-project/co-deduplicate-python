const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs-extra');
const { errorList, handleError } = require('./error');

const business = {};

business.beforeAnyJob = (callback) => {
  let error;
  const pythonProcess = spawn('python3', ['--version']);

  pythonProcess.on('error', (err) => {
    if (err.code === 'ENOENT') {
      error = new Error('Python is not installed on the system.');
    } else {
      error = err;
    }
  });

  pythonProcess.on('close', (code) => callback(error));
};

business.doTheJob = (docObject, callback) => {
  const data = [docObject];
  const pathToTmpDocObject = path.join(__dirname, 'tmpDocObject.json');
  const pathToPythonScript = path.join(__dirname, 'pythonScripts', 'expand.py');

  fs.outputFile(pathToTmpDocObject, JSON.stringify(data), 'utf-8', (err) => {
    if (err) return callback(handleError(docObject, errorList.WriteFileError, err));

    let duplicates;
    const pythonProcess = spawn('python3', [pathToPythonScript, '-f', pathToTmpDocObject]);

    pythonProcess.stdout.on('data', (duplicatesString) => {
      duplicates = JSON.parse(duplicatesString).duplicates;
    });

    pythonProcess.on('close', (code) => {
      duplicates.forEach((duplicate) => {
        const found = docObject.duplicates.find((dupInDocObject) => dupInDocObject.sourceUid === duplicate.sourceUid);
        if (!found) docObject.duplicates.push(duplicate);
      });

      fs.unlink(pathToTmpDocObject, (err) => {
        if (err) console.error(`Could not delete ${pathToTmpDocObject}.`);

        return callback();
      });
    });
  });
};

module.exports = business;
