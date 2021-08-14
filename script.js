'use strict';

(async () => {
	const response = await fetch('times.json');
	const times = await response.json();

	const text = times.map(([ts, ms]) => `${ts}\t${ms} ms`).join('\n');
	document.querySelector('section').innerText = text;

	const chart = c3.generate({
		'bindto': '#chart',
		'data': {
			'type': 'area',
			'x': 'x',
			'columns': [],
		},
		'axis': {
			'x': {
				'type': 'timeseries',
				'tick': {'format': '%a %H:%M'}, // https://github.com/d3/d3-time-format#locale_format
			},
		},
		'legend': {'show': false},
	});
	const columns = [
		['x', ...times.map(([ts, ms]) => new Date(ts + 'Z'))],
		['ms', ...times.map(([ts, ms]) => ms)],
	];
	chart.load({'columns': columns});
})();
