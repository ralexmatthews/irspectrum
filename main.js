'use strict';

const express = require('express'),
	app = express();

let bodyParser = require('body-parser');
const formidable = require('formidable');
const path = require('path');
const fs = require('fs');
const spawn = require('child_process').spawn;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
	extended: true,
}));

app.use('/favicon.ico', express.static('./public/favicon.ico'));

// Setup our static resources folder
app.use(express.static('public'));

// Setup Pug
app.set('view engine', 'pug');
app.set('views', './views');

// Setup views
app.get('/', function (req, res) {
	res.render('home');
});

app.get('/aboutus', function (req, res) {
	res.render('aboutus');
});

app.post('/getmatch', function (req, res) {
	// set up recieving file
	let form = new formidable.IncomingForm();
	form.multiples = false;
	form.uploadDir = path.join(__dirname, '/temp');
	let filepath;

	// parse the incoming file
	form.parse(req);

	// save the file as its name in the /temp folder
	form.on('file', (field, file) => {
		filepath = path.join(form.uploadDir, file.name);
		fs.rename(file.path, filepath, err => {
			if (err) {
				console.log(err);
			}
		});
	});

	// if something wonky happens
	form.on('error', function (err) {
		console.log('An error has occured: \n' + err);
	});

	// once its finished saving, do the business. This is where the magic comparing happens
	form.on('end', () => {
		runJoshsPython(filepath, res);
	});
});

// Start the server and have it listen on a port
const server = app.listen(3000, function () {
	console.log(`Server started on port ${server.address().port}!`);
});

// this function runs the python programs
let runJoshsPython = function (pathToPDF, res) {
	// run 'Pull Data From PDF.py' with the path to the file
	const pythonFile = spawn('python', ['IRSpectrum.py', pathToPDF,"-query"]);

	// if something wonky happens let me know
	pythonFile.on('error', err => {
		console.log(err);
	});

	let pathToQuery="";
	// once the program gives any output
	pythonFile.stdout.on('data', chunk => {
		// format output
		pathToQuery = chunk.toString('utf8');

	});

	// once it's finished running
	pythonFile.on('close', () => {
		// run 'Compare to Query.py'
		const comparePy = spawn('python', ['CompareQueryToDB.py',pathToQuery]);

		// if something wonky happens let me know
		comparePy.on('error', err => {
			console.log('error:', err);
		});

		// if the program has an exception let me know
		comparePy.on('uncaughtException', function(err) {
			console.log('Caught exception: ' + err);
		});

		// once the program gives any output
		comparePy.stdout.on('data', chunk => {
			// format output
			let textchunk = chunk.toString('utf8');

			// send results back to browser
			returnResults(textchunk, res);
		});
	});
};

// this function returns the results back to the browser
let returnResults = function (winners, res) {
	// split string of winners into array
	winners = winners.split(' ');

	// send back JSON of first 4 winners
	res.send(JSON.stringify({
		1: winners[0],
		2: winners[1],
		3: winners[2],
		4: winners[3],
	}));
};
