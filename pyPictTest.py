from pypict import *
import os


def filename_check_Test():
    assert filename_check("Caribou") == "Caribou"
    with open("FichierTest.txt") as f_out:
        f_out.write(" ")
    assert filename_check("FichierTest.txt") == "FichierTest (2).txt"
    with open("FichierTest (2).txt") as f_out:
        f_out.write(" ")
    assert filename_check("FichierTest (2).txt") == "FichierTest (3).txt"
    # TODO : tests with files without extension and files with "."
