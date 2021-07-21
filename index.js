const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs-extra');

const business = {};

business.doTheJob = (docObject, callback) => {
  const data = [docObject];
  const pathToTmpDocObject = path.join(__dirname, 'tmpDocObject.json');
  const pathToPythonScript = path.join(__dirname, 'pythonScripts', 'expand.py');

  fs.outputFile(path.join(__dirname, 'tmpDocObject.json'), JSON.stringify(data), 'utf-8', (err) => {
    if (err) throw err;

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
        if (err) throw err;

        return callback();
      });
    });
  });
};

module.exports = business;
