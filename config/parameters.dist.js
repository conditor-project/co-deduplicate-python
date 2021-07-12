module.exports = {
  get: () => {
    return {
      host: process.env.CO_DUPLICATES_HOST ? process.env.CO_DUPLICATES_HOST : 'co-autodeduplicates-1.tdmservices.intra.inist.fr',
      uri: 'expand',
      port: process.env.CO_DUPLICATES_PORT ? process.env.CO_DUPLICATES_PORT : 80,
      retry: {
        times: 3,
        interval: 3000,
      },
    };
  },
};
