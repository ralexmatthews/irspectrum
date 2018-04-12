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
