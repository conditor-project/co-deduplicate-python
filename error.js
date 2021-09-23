const errorList = {
  JSONParsingError: 'JSONParsingError',
  MalformedDocObjectError: 'MalformedDocObjectError',
  MissingDuplicatesKeyError: 'MissingDuplicatesKeyError',
  WriteFileError: 'WriteFileError',
};

const list = [
  {
    name: errorList.JSONParsingError,
    handle: (err, docObject) => {
      err.message = 'Syntax error in JSON returned by the Python script.';

      docObject.errCode = errorList.JSONParsingError;
      docObject._errMsg = 'Erreur de syntaxe dans le JSON renvoyé par le script Python.';

      return err;
    },
  },
  {
    name: errorList.MissingDuplicatesKeyError,
    handle: (err, docObject) => {
      err.message = 'The JSON returned by the Python script does not contain a \'duplicates\' array.';

      docObject.errCode = errorList.MissingDuplicatesKeyError;
      docObject._errMsg = 'Le JSON renvoyé par le script Python ne contient pas de tableau \'duplicates\'.';

      return err;
    },
  },
  {
    name: errorList.MalformedDocObjectError,
    handle: (err, docObject) => {
      docObject.errCode = errorList.MalformedDocObjectError;
      docObject._errMsg = `Le script Python a renvoyé une erreur: ${err.message}`;

      return err;
    },
  },
  {
    name: errorList.WriteFileError,
    handle: (err, docObject) => {
      docObject.errCode = errorList.WriteFileError;
      docObject._errMsg = `Impossible d'écrire un fichier au chemin ${err.path}.`;

      return err;
    },
  },
];

/**
 * Creates the `Error` instance the pass to doTheJob's callback.
 * @param {object} docObject The `docObject` provided by the previous module.
 * @param {string} errName The name of the `Error` instance to create (member `name` of `Error` class).
 * @param {Error} originalErr The original `Error` instance.
 * @returns {Error} The new `Error` instance or the original one if it was provided.
 */
function handleError (docObject, errName, originalErr = null) {
  // Looks for the appropriate error handler
  const errInfo = list.find((err) => err.name === errName);

  let err = originalErr;
  if (!err) err = new Error();
  if (errName) err.name = errName;

  if (!errInfo) {
    docObject.errCode = err.name ? err.name : 'Error';
    docObject._errMsg = err.message;
    return err;
  }

  return errInfo.handle(err, docObject);
}

module.exports = {
  errorList,
  handleError,
};
