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

	// create html stuff
	let div = document.createElement('div');
	let displayImage = document.createElement('img');
	displayImage.src = window.URL.createObjectURL(imageInput);
	displayImage.classList.add('resize');
	displayImage.id = 'displayPic';
	document.getElementById('filename').innerText = input.files[0].name;

	// this is the thingy that allows us to display the image on screen
	let uFile;

	// if there is already a picture there, just update it
	if (document.getElementById('displayPic')) {
		document.getElementById('displayPic').src = window.URL.createObjectURL(imageInput);
		uFile = window.URL.createObjectURL(imageInput);
	}
	// else just create the picture
	else {
		document.body.appendChild(div);
		div.appendChild(displayImage);
		document.getElementById('findButton').classList = 'btn btn-primary';
		uFile = window.URL.createObjectURL(imageInput);
	}
};

// This is where we send the picture to the server and the server will do the comparison
// and reply with the matches somehow.
document.getElementById('findButton').addEventListener('click', function () {
	// grab ahold of the image file
	let imageInput = input.files[0];

	let myData = new FormData();
	myData.append('file', imageInput);

	$.ajax({
		url: 'http://localhost:3000/getmatch',
		data: myData,
		processData: false,
		contentType: false,
		type: 'POST',
		complete: function (data) {
			let response = JSON.parse(data.responseText);

			let winnersContainer = document.createElement('div');
			let winner1 = document.createElement('div');
			let winner2 = document.createElement('div');
			let winner3 = document.createElement('div');
			let winner4 = document.createElement('div');

			winner1.innerText = '1. ' + response['1'];
			winner2.innerText = '2. ' + response['2'];
			winner3.innerText = '3. ' + response['3'];
			winner4.innerText = '4. ' + response['4'];

			winnersContainer.appendChild(winner1);
			winnersContainer.appendChild(winner2);
			winnersContainer.appendChild(winner3);
			winnersContainer.appendChild(winner4);

			winnersContainer.id = 'winners';

			// if there is already a picture there, just update it
			if (document.getElementById('winners')) {
				document.body.removeChild(document.getElementById('winners'));
				document.body.appendChild(winnersContainer);
			}
			// else just create the picture
			else {
				document.body.appendChild(winnersContainer);
			}
		}
	});

});