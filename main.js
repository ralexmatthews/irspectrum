'use strict';

const express = require('express'),
	app = express();

let bodyParser = require('body-parser');
const data = require('./src/values.json');
const formidable = require('formidable');
const path = require('path');
const fs = require('fs');
const getpixels = require('get-pixels');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
	extended: true,
}));

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
		setTimeout(() => {
			// get pixels in the form pixelsArray[x][y] = [r, g, b, a]
			let pixelsArray = getArrayPixels(filepath);

			// pause for a 1/20th of a second for the function above to work
			setTimeout(() => {
				// alrighty boys. This is where the search function is going to be.

				// arrays for algorithm
				let compare = [];
				let differences = [];

				// height array for user uploaded file
				let original = getHeightGraph(pixelsArray);

				// load arrays from JSON
				for (let element in data) {
					compare.push(getHeightGraph(data[element]));
				}

				compare.forEach(element => {
					let sum = 0;
					for (let x = 0; x < element.length; x++) {
						sum += Math.abs(original[x] - element[x]);
					}
					differences.push(sum);
				});

				// create object with key=height, value=name pairs to find winners
				let names = Object.getOwnPropertyNames(data);
				let winners = {};
				let counter = 0;
				differences.forEach(difference => {
					winners[difference] = names[counter];
					counter++;
				});

				names = Object.getOwnPropertyNames(winners);

				res.send(JSON.stringify({
					1: winners[names[0]],
					2: winners[names[1]],
					3: winners[names[2]],
					4: winners[names[3]],
				}));
			}, 50);
		}, 50);
	});
});

// Start the server and have it listen on a port
const server = app.listen(3000, function () {
	console.log(`Server started on port ${server.address().port}!`);
});

// this function gets the pixels of the image of the specified path
let getArrayPixels = function (imagepath) {

	// set up arrays
	let otherData = [],
		yarray = [],
		pixel = [];

	// get pixels in raw form
	getpixels(imagepath, function (err, pixels) {

		// convaluted way to get pixels in the easy form
		for (let x = 0; x < 1024; x++) {
			for (let y = 0; y < 768; y++) {
				for (let z = 0; z < 4; z++) {
					pixel.push(pixels.get(x, y, z));
				}
				yarray.push(pixel);
				pixel = [];
			}
			otherData.push(yarray);
			yarray = [];
		}
	});
	return otherData;
};

let getHeightGraph = function (imageArray) {
	let heightGraph = [];

	for (let x = 155; x < 850; x++) {
		let black = false;
		let y = 724;

		while (!black) {
			if (y < 0) {
				y = 724;
				black = true;
				heightGraph.push(y);
			} else if (imageArray[x][y][0] < 25) {
				black = true;
				heightGraph.push(y);
			} else {
				y--;
			}
		}
	}

	return heightGraph;
};