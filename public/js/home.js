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

	if (ext == 'jpg' || ext == 'pdf') {
		// create html stuff
		let span = document.createElement('span');
		let displayImage = document.createElement('img');
		if (ext == 'jpg') {
			displayImage.src = window.URL.createObjectURL(imageInput);
		} else {
			displayImage.src = 'http://localhost:3000/images/pdf.png';
		}
		displayImage.classList.add('resize');
		span.id = 'displayPic';
		document.getElementById('filename').innerText = input.files[0].name;

		// if there is already a picture there, remove it
		if (document.getElementById('displayPic')) {
			document.body.removeChild(document.getElementById('displayPic'));
		}

		document.body.appendChild(span);
		span.appendChild(displayImage);
	}

	// enable the find button once file is uploaded
	document.getElementById('findButton').classList = 'btn btn-primary';
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

			// create all the html stuff we need
			let winnersContainer = document.createElement('span');
			let winner1 = document.createElement('span');
			let winner2 = document.createElement('span');
			let winner3 = document.createElement('span');
			let winner4 = document.createElement('span');
			let winner1pic = document.createElement('img');
			let winner2pic = document.createElement('img');
			let winner3pic = document.createElement('img');
			let winner4pic = document.createElement('img');
			let winner1button = document.createElement('span');
			let winner2button = document.createElement('span');
			let winner3button = document.createElement('span');
			let winner4button = document.createElement('span');
			let winnerButtonContainer = document.createElement('span');

			winnerButtonContainer.id = 'winnerButtonContainer';

			// add all winner buttons to the container
			winnerButtonContainer.appendChild(winner1button);
			winnerButtonContainer.appendChild(winner2button);
			winnerButtonContainer.appendChild(winner3button);
			winnerButtonContainer.appendChild(winner4button);

			// make them all pretty buttons
			winner1button.classList = 'btn btn-primary graphbuttons';
			winner2button.classList = 'btn btn-primary graphbuttons';
			winner3button.classList = 'btn btn-primary graphbuttons';
			winner4button.classList = 'btn btn-primary graphbuttons';

			// add the winner names to the buttons and labels
			winner1.innerText = '1. ' + response['1'];
			winner2.innerText = '2. ' + response['2'];
			winner3.innerText = '3. ' + response['3'];
			winner4.innerText = '4. ' + response['4'];
			winner1button.innerText = '1. ' + response['1'];
			winner2button.innerText = '2. ' + response['2'];
			winner3button.innerText = '3. ' + response['3'];
			winner4button.innerText = '4. ' + response['4'];

			// get the pictures from the server
			winner1pic.src = 'http://localhost:3000/images/' + response['1'] + '.jpg';
			winner2pic.src = 'http://localhost:3000/images/' + response['2'] + '.jpg';
			winner3pic.src = 'http://localhost:3000/images/' + response['3'] + '.jpg';
			winner4pic.src = 'http://localhost:3000/images/' + response['4'] + '.jpg';

			// make the pictures the right size
			winner1pic.classList = 'resize';
			winner2pic.classList = 'resize hidden';
			winner3pic.classList = 'resize hidden';
			winner4pic.classList = 'resize hidden';
			winner1.classList = 'name';
			winner2.classList = 'hidden name';
			winner3.classList = 'hidden name';
			winner4.classList = 'hidden name';

			winnersContainer.appendChild(winner1);
			winnersContainer.appendChild(winner1pic);
			winnersContainer.appendChild(winner2);
			winnersContainer.appendChild(winner2pic);
			winnersContainer.appendChild(winner3);
			winnersContainer.appendChild(winner3pic);
			winnersContainer.appendChild(winner4);
			winnersContainer.appendChild(winner4pic);

			winnersContainer.id = 'winners';

			// if there is already a picture there, just update it
			if (document.getElementById('winners')) {
				document.body.removeChild(document.getElementById('winners'));
				document.body.appendChild(winnersContainer);
				document.getElementById('buttonholder').removeChild(document.getElementById('winnerButtonContainer'));
				document.getElementById('buttonholder').appendChild(winnerButtonContainer);
			}
			// else just create the picture
			else {
				document.body.appendChild(winnersContainer);
				document.getElementById('buttonholder').appendChild(winnerButtonContainer);
			}

			winner1button.addEventListener('click', () => {
				winner1.classList.remove('hidden');
				winner2.classList.add('hidden');
				winner3.classList.add('hidden');
				winner4.classList.add('hidden');
				winner1pic.classList.remove('hidden');
				winner2pic.classList.add('hidden');
				winner3pic.classList.add('hidden');
				winner4pic.classList.add('hidden');
			});

			winner2button.addEventListener('click', () => {
				winner1.classList.add('hidden');
				winner2.classList.remove('hidden');
				winner3.classList.add('hidden');
				winner4.classList.add('hidden');
				winner1pic.classList.add('hidden');
				winner2pic.classList.remove('hidden');
				winner3pic.classList.add('hidden');
				winner4pic.classList.add('hidden');
			});

			winner3button.addEventListener('click', () => {
				winner1.classList.add('hidden');
				winner2.classList.add('hidden');
				winner3.classList.remove('hidden');
				winner4.classList.add('hidden');
				winner1pic.classList.add('hidden');
				winner2pic.classList.add('hidden');
				winner3pic.classList.remove('hidden');
				winner4pic.classList.add('hidden');
			});

			winner4button.addEventListener('click', () => {
				winner1.classList.add('hidden');
				winner2.classList.add('hidden');
				winner3.classList.add('hidden');
				winner4.classList.remove('hidden');
				winner1pic.classList.add('hidden');
				winner2pic.classList.add('hidden');
				winner3pic.classList.add('hidden');
				winner4pic.classList.remove('hidden');
			});
		}
	});

});