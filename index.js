const path = require('path');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs-extra');
const _ = require('lodash');
const VError = require('verror');
const { errorList, handleError } = require('./error');

const business = {};

business.doTheJob = (docObject, callback) => {
  const data = [docObject];
  const pathToTmpDocObject = path.join(__dirname, 'tmpDocObject.json');
  const pathToPythonScript = path.join(__dirname, 'pythonScripts', 'expand.py');

  fs.outputFile(pathToTmpDocObject, JSON.stringify(data), 'utf-8', (err) => {
    if (err) return callback(handleError(docObject, errorList.WriteFileError, err));

    let errInPythonProcess;
    let duplicates;
    const pythonProcess = spawn('python3', [pathToPythonScript, '-f', pathToTmpDocObject]);

    pythonProcess.stdout.on('data', (duplicatesString) => {
      let jsonParsed;
      try {
        jsonParsed = JSON.parse(duplicatesString);
      } catch (error) {
        errInPythonProcess = handleError(docObject, errorList.JSONParsingError);
        return;
      }

      if (!jsonParsed.duplicates || !_.isArray(jsonParsed.duplicates)) {
        errInPythonProcess = handleError(docObject, errorList.MissingDuplicatesKeyError);
        return;
      }

      duplicates = jsonParsed.duplicates;
    });

    pythonProcess.on('close', (code) => {
      if (errInPythonProcess) return callback(errInPythonProcess);

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

business.beforeAnyJob = (callback) => {
  const requirementsFilePath = path.join(__dirname, 'pythonScripts', 'requirements.txt');

  if (!fs.existsSync(requirementsFilePath)) {
    return callback(new Error('Requirements file not found'));
  }

  const errors = [];
  let finalError;

  const processes = [
    spawnSync('python3', ['--version']),
    spawnSync('pip', ['install', '-r', path.join(__dirname, 'pythonScripts', 'requirements.txt')]),
  ];

  processes.forEach((process) => {
    const processError = getProcessError(process);
    if (processError) errors.push(processError);
  });

  if (!_.isEmpty(errors)) finalError = VError.errorFromList(errors);

  return callback(finalError);
};

/**
 * Gets an error from a process and creates a more specific one if possible.
 * @param {object} process The process.
 * @returns {Error|null} If found, the error, `null` otherwise.
 */
function getProcessError (process) {
  let finalError = null;

  if (process.error) {
    if (process.error.code === 'ENOENT') {
      finalError = new VError(process.error, `${process.error.path} is not installed on the system`);
    } else {
      finalError = process.error;
    }
  }

  return finalError;
}

module.exports = business;
