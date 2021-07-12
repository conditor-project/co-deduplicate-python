const request = require('request');

const data = [
  { id: 0, value: { volume: '43', pageRange: '2109-2114', duplicates: [{ sourceUid: 'crossref$10.1007/s11664-014-2982-z', sessionName: 'CROSSREF_2021-01-05_2014_1', rules: ['Article : 1ID:doi+TiC_ENG', 'Article : 1ID:doi+TiC'], source: 'crossref', idConditor: '1sZqglsAiAXBZMeTynDh6fL77' }], sourceUid: 'hal$hal-00994781', issn: ['0361-5235'], documentType: ['ART'], isbn: [], typeConditor: 'Article', eissn: ['1543-186X'], title: { default: 'Unconventional thin-film thermoelectric converters : structure, simulation, and comparative study', monography: '', journal: 'Journal of Electronic Materials', en: 'Unconventional thin-film thermoelectric converters : structure, simulation, and comparative study', fr: '', meeting: '' }, publicationDate: '2014', doi: '10.1007/s11664-014-2982-z', _score: 0.7896045, _sort: [12200877] } },
];

console.log(Buffer.from(JSON.stringify(data)).toString());

request({
  method: 'POST',
  uri: 'http://co-autodeduplicates-1.tdmservices.intra.inist.fr/expand',
  body: Buffer.from(JSON.stringify(data)),
  encoding: null,
}, (err, response, body) => {
  if (err) throw err;

  console.log(body.toString());
});
