import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from extractor import extract
from rules import evaluate
from advisor import advise
from models import ScreeningReport


class ScreeningPipeline:
    def run(self, listing_text: str) -> ScreeningReport:
        financials = extract(listing_text)
        evaluation = evaluate(financials)
        return advise(financials, evaluation)
