"""
Unit tests for ICAO 9303 7-3-1 weighting check digit calculation.
"""
import pytest
from backend.app.services.mrz_service import calculate_mrz_check_digit

def test_calculate_mrz_check_digit_numeric():
    # 8*7 + 9*3 + 0*1 + 5*7 + 1*3 + 4*1 = 125 % 10 = 5
    assert calculate_mrz_check_digit("890514") == 5

def test_calculate_mrz_check_digit_alphanumeric():
    # E84920194 -> 3
    assert calculate_mrz_check_digit("E84920194") == 3

def test_calculate_mrz_check_digit_filler():
    # Fillers '<' are treated as 0
    assert calculate_mrz_check_digit("<<<") == 0
