from ..abstract_test import AbstractTestContract
import math


class TestContract(AbstractTestContract):
    """
    run test with python -m unittest contracts.tests.market_makers.test_calc_shares
    """

    def __init__(self, *args, **kwargs):
        super(TestContract, self).__init__(*args, **kwargs)
        self.deploy_contracts = [self.lmsr_name, self.math_library_name]

    @staticmethod
    def calc_shares(tokens, outcome, share_distribution, initial_funding):
        _max = max(share_distribution)
        share_distribution = [_max - x for x in share_distribution]
        b = initial_funding/float(math.log(len(share_distribution)))
        return b * math.log(
            sum([math.exp(share_count / b + tokens / b) for share_count in share_distribution]) -
            sum([math.exp(share_count / b) for index, share_count in enumerate(share_distribution) if index != outcome])
        ) - share_distribution[outcome]

    def test(self):
        # Calculating costs for buying shares and earnings for selling shares
        outcome = 1
        opposite_outcome = 0
        initial_funding = self.MIN_MARKET_BALANCE
        share_distribution = [initial_funding, initial_funding]
        number_of_shares = 5*10**18
        tokens = self.lmsr.calcCostsBuying(
            "".zfill(64).decode('hex'), initial_funding, share_distribution, outcome, number_of_shares
        )
        approx_number_of_shares = self.calc_shares(tokens, outcome, share_distribution, initial_funding)
        self.assertAlmostEqual(number_of_shares/approx_number_of_shares, 1, 3)
        # Market maker increases shares of the opposite outcome
        share_distribution[outcome] += tokens - number_of_shares
        share_distribution[opposite_outcome] += tokens
        # Calculating costs for buying shares and earnings for selling shares
        number_of_shares = 5 * 10 ** 18
        tokens = self.lmsr.calcCostsBuying(
            "".zfill(64).decode('hex'), initial_funding, share_distribution, outcome, number_of_shares
        )
        approx_number_of_shares = self.calc_shares(tokens, outcome, share_distribution, initial_funding)
        self.assertAlmostEqual(number_of_shares / approx_number_of_shares, 1, 3)
