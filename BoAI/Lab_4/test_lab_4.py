import pytest
import os
import sys

sys.path.append(r"D:/Programming/PythonApplications")
from BoAI.Lab_4.lab_4 import load_and_preprocess, count_shapes_on_image

IMAGES_DIR = r"D:/Programming/PythonApplications/BoAI/Lab_4/test_images"

TEST_CASES = [
    ("test_0.jpg", 2, 2),
    ("test_1.jpg", 1, 2),
    ("test_2.jpg", 1, 1),
    ("test_3.jpg", 2, 1),
    ("test_4.jpg", 1, 1),
    ("test_5.jpg", 1, 3),
    ("test_6.jpg", 6, 3),
    ("test_7.jpg", 0, 9),
    ("test_8.jpg", 6, 3),
    ("test_9.jpg", 2, 2),
]

@pytest.mark.parametrize("filename, exp_q, exp_c", TEST_CASES)
def test_shapes(filename, exp_q, exp_c):
    path = os.path.join(IMAGES_DIR, filename)
    assert os.path.exists(path), f"File not found: {filename}"

    binary = load_and_preprocess(path)
    assert binary is not None, "Image load failed"
    
    res = count_shapes_on_image(binary)

    err_q = f"\n{filename} [Quads]   | Expected: {exp_q} | Found: {res['quads']}"
    assert res['quads'] == exp_q, err_q

    err_c = f"\n{filename} [Circles] | Expected: {exp_c} | Found: {res['circles']}"
    assert res['circles'] == exp_c, err_c