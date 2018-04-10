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
#from compareQueryToDB import compareQueryToDB
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------

#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def main(queryData):
    formatPDFData(queryData)

    #result = compareQueryToDB()

    #print(result)

    sys.stdout.flush()

#cd desktop/irspectrum-joshh-db

main(sys.argv[1])
#---------------------------------End of Program-------------------------------
