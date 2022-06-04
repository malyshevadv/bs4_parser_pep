# constants.py
from pathlib import Path


MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEP_DOC_URL = 'https://peps.python.org/'

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}


STATUS_LIST = {
    'Active': 0,
    'Accepted': 1,
    'Deferred': 2,
    'Final': 3,
    'Provisional': 4,
    'Rejected': 5,
    'Superseded': 6,
    'Withdrawn': 7,
    'Draft': 8,
}
