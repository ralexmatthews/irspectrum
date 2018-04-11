"""
Program: IRSpectrum.py
Programmed by: Josh Ellis, Josh Hollingsworth, Aaron Kruger, Alex Matthews, and
    Joseph Sneddon
Description: This program will recognize the IR Spectrum Analysis of an unknown
    molecule and compare that analysis to a database of known molecules and
    their IR Spectrum Analysis.
"""
#---------------------------------Imports--------------------------------------
import sys
from FormatPDFData import formatPDFData
from CompareQueryToDB import compareQueryToDB
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
"""let runJoshsPython = function (pathToPDF, res) {
	// run 'Pull Data From PDF.py' with the path to the file
	const pythonFile = spawn('python', ['IRSpectrum.py', pathToPDF,"-query"]);

	// if something wonky happens let me know
	pythonFile.on('error', err => {
		console.log(err);
	});

	//let pathToQuery="";
	// once the program gives any output
	pythonFile.stdout.on('data', chunk => {
		// format output
		pathToQuery = chunk.toString('utf8');

	});

	// once it's finished running
	pythonFile.on('close', () => {

		pythonFile.on('uncaughtException', function(err) {
			console.log('Caught exception: ' + err);
		});

		pythonFile.stdout.on('data', chunk => {
			// format output
			let textchunk = chunk.toString('utf8');

			// send results back to browser
			returnResults(textchunk, res);
		});

		// run 'Compare to Query.py'
		//const comparePy = spawn('python', ['Compare To Query.py',pathToQuery]);

		// if something wonky happens let me know
		//comparePy.on('error', err => {
			//console.log('error:', err);
		//});

		// if the program has an exception let me know
		//comparePy.on('uncaughtException', function(err) {
			//console.log('Caught exception: ' + err);
		//});

		// once the program gives any output
		//comparePy.stdout.on('data', chunk => {
			// format output
			//let textchunk = chunk.toString('utf8');

			// send results back to browser
			//returnResults(textchunk, res);
		//});
	});
};"""
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def main(queryData):
    formatPDFData(queryData)

    results = compareQueryToDB()

    print(result)

    sys.stdout.flush()

    #print(test)

#cd Documents/GitHub/irspectrum

main(sys.argv[1])
#---------------------------------End of Program-------------------------------
