import os
import sys
import json
import unittest

# Set path for importing deduplicate module
parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parentDirectory)

from deduplicate.deduplicate import Record
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Check if docObject contains idConditor and sourceUid
record1 = {"idConditor" : "XXXXX", "sourceUid" :  "XXXXX"}
record1_error_code = 100

# Check if docObject contains sourceUid and not idConditor
record2 = {"sourceUid" :  "XXXXX"}
record2_error_code = 102

# Check if docObject contains idConditor and not sourceUid
record3 = {"idConditor" : "XXXXX"}
record3_error_code = 101

# Empty docObject
record4 = {}
record4_error_code = 103

# Other type of input
record5 = []
record6 = "This a test for string input"
record_error_code = 104

# Import true Object
with open(os.path.join(parentDirectory, "tests/test.json"), encoding="utf8") as f :
    record7 = json.load(f)[0]


class Test(unittest.TestCase) :

    def test_idConditor_and_sourceUid(self) :
        rc1 = Record(record1)
        tt = rc1.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record1_error_code)

    def test_not_idConditor(self) :
        rc2 = Record(record2)
        tt = rc2.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record2_error_code)

    def test_not_sourceUid(self) :
        rc3 = Record(record3)
        tt = rc3.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record3_error_code)

    def test_empty_docObject(self) :
        rc4 = Record(record4)
        tt = rc4.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record4_error_code)

    def test_input_list(self) :
        rc5 = Record(record6)
        tt = rc5.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record_error_code)

    def test_input_string(self) :
        rc6 = Record(record6)
        tt = rc6.deduplicate()
        self.assertEqual(tt.get('error').get("code"), record_error_code)

    def test_deduplicate(self) :
        rc7 = Record(record7)
        tt = rc7.deduplicate()
        self.assertEqual(type(tt), list)
if __name__ == "__main__" :
    unittest.main()
