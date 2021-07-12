const fs = require('fs-extra');
const path = require('path');

/**
 * Gets the config file path.
 * @returns {string} The path to the config file.
 */
function getConfigPath () {
  const defaultConfigPath = path.join(__dirname, 'parameters.dist.js');
  const overwrittenConfigPath = path.join(__dirname, 'parameters.js');

  if (fs.existsSync(overwrittenConfigPath)) return overwrittenConfigPath;
  else if (fs.existsSync(defaultConfigPath)) return defaultConfigPath;

  const err = new Error('No config file was found.');
  err.name = 'ConfigNotFoundError';

  throw err;
}

/**
 * Creates the Grobid service URL.
 * @param {object} config The config object.
 * @returns {string} The Grobid service URL as a string.
 */
function buildServiceURL (config) {
  return `http://${config.host}:${config.port}/${config.uri}`;
}

module.exports = {
  getConfigPath,
  buildServiceURL,
};
