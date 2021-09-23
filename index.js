const path = require('path');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs-extra');
const _ = require('lodash');
const VError = require('verror');
const { errorList, handleError } = require('./error');

const business = {};

business.doTheJob = (docObject, callback) => {
  const data = [docObject];
  const pathToPythonScript = path.join(__dirname, 'pythonScripts', 'main.py');

  let errInPythonProcess;
  let duplicates;
  const pythonProcess = spawn('python3', [pathToPythonScript, JSON.stringify(data)]);

  pythonProcess.stdout.on('data', (duplicatesString) => {
    try {
      duplicates = JSON.parse(duplicatesString.toString());
    } catch (error) {
      errInPythonProcess = handleError(docObject, errorList.JSONParsingError);
      return;
    }

    if (!duplicates || !_.isArray(duplicates)) {
      errInPythonProcess = handleError(docObject, errorList.MissingDuplicatesKeyError);
    }
  });

  pythonProcess.stderr.on('data', (errString) => {
    let errParsed;
    try {
      errParsed = JSON.parse(errString.toString()).error;
    } catch (error) {
      errInPythonProcess = handleError(docObject, errorList.JSONParsingError);
      return;
    }

    const err = new Error(errParsed.message);
    err.name = errParsed.type;
    errInPythonProcess = handleError(docObject, errorList.MalformedDocObjectError, err);
  });

  pythonProcess.on('close', (code) => {
    if (errInPythonProcess) return callback(errInPythonProcess);

    duplicates.forEach((duplicate) => {
      const found = docObject.duplicates.find((dupInDocObject) => dupInDocObject.sourceUid === duplicate.sourceUid);
      if (!found) docObject.duplicates.push(duplicate);
    });

    return callback();
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
