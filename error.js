const errorList = {
  HttpError: 'HttpError',
  MissingDataError: 'MissingDataError',
  NetworkError: 'NetworkError',
};

const list = [
  {
    name: errorList.HttpError,
    handle: (err, docObject) => {
      err.message = `HTTP error with status code: ${err.code}.`;

      docObject.errCode = errorList.HttpError;
      docObject._errMsg = 'Données manquante dans le docObject.';

      return err;
    },
  },
  {
    name: errorList.NetworkError,
    handle: (err, docObject) => {
      err.message = 'Network error.';

      docObject.errCode = errorList.NetworkError;
      docObject._errMsg = 'Erreur réseau.';

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
