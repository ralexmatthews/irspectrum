'use strict';

// html css bootstrap updating
let tab = document.getElementById('home');
tab.classList.add('active');

// grabs a hold of the input for use later
let input = document.getElementById('fileInput');

// allows the input button to look pretty
document.getElementById('selectFile').addEventListener('click', function () {
	input.click();
});

// displays the image when you click select file
input.onchange = function () {
	// gets a hold of the image
	let imageInput = input.files[0];

	let ext = imageInput.name.substring(imageInput.name.length - 3);

	if (ext == 'pdf' || ext == 'jpg') {
		// create html stuff
		document.getElementById('filename').innerText = input.files[0].name;
	} else {
		document.getElementById('filename').innerText = 'Invalid File';
	}

	// enable the find button once file is uploaded
	document.getElementById('findButton').classList = 'btn btn-primary';
};

// This is where we send the picture to the server and the server will do the comparison
// and reply with the matches somehow.
document.getElementById('findButton').addEventListener('click', function () {
	let imageInput = input.files[0];
	let ext = imageInput.name.substring(imageInput.name.length - 3);
	if (ext == 'pdf' || ext == 'jpg') {
		// show spinny wheel until finished
		document.body.style.cursor = 'wait';

		// prepare file to be sent
		let myData = new FormData();
		myData.append('file', imageInput);

		// send file to server
		$.ajax({
			url: 'http://' + location.host + '/getmatch',
			data: myData,
			processData: false,
			contentType: false,
			type: 'POST',
			complete: function (data) {
				let response = JSON.parse(data.responseText);

				// create all the html stuff we need
				let winnersContainer = document.createElement('span');
				let winnersList = document.createElement('ul');
				winnersList.classList.add('list-group');

				let winnerULS = [];

				for (let i = 0; i < 20; i++) {
					let li = document.createElement('li');
					li.classList.add('list-group-item');
					li.innerText = response[i + 1];
					li.addEventListener('click', updateResults);
					winnerULS.push(li);
				}

				for (let i = 0; i < 20; i++) {
					winnersList.appendChild(winnerULS[i]);
				}

				winnersContainer.appendChild(winnersList);
				winnersContainer.classList.add('floatleft');
				document.body.appendChild(winnersContainer);

				let uploaded = document.createElement('img');
				uploaded.src = '/images/temp.jpg';
				uploaded.classList.add('resize');

				document.body.appendChild(uploaded);

				let resultsSpan = document.createElement('span');
				resultsSpan.classList.add('card');
				let resultsImg = document.createElement('img');
				resultsImg.id = 'resultsImage';
				resultsImg.classList.add('resize');
				resultsImg.classList.add('card-img-top');
				resultsImg.src = '/images/' + response[1] + '.jpg';
				let info = document.createElement('div');
				info.classList.add('card-body');
				let name = document.createElement('h5');
				name.innerText = response[1];
				name.id = 'name';
				info.appendChild(name);

				resultsSpan.appendChild(resultsImg);
				resultsSpan.appendChild(info);
				document.body.appendChild(resultsSpan);

				// set cursor back to normal
				document.body.style.cursor = 'default';
			}
		});
	}
});

let updateResults = evt => {
	$(' #resultsImage ').attr('src', '/images/' + evt.target.innerText + '.jpg');
	$(' #name ').text(evt.target.innerText);
};