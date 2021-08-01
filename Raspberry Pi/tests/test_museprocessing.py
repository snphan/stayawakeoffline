import pytest
'''
Unittest the output of your functions here using pytest
'''

# Add the parent directory to the list of module search paths
import os, sys
p = os.path.abspath('.')
sys.path.insert(1, p)


# Imports from modules to be tested
import museprocessing.preprocessing as prep

def test_answer():
    assert prep.add(2,3) == 5