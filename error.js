const errorList = {
  JSONParsingError: 'JSONParsingError',
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
