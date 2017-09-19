from settings import *
import scipy.stats
import scipy.integrate
import numpy as np


class Campaign(object):

    def __init__(self, name, train_data, test_data, pctr_data):
        self.original_ecpc = 0.  # original eCPC from train data
        self.original_ctr = 0.  # original ctr from train data
        self.test_clicks_prices = []  # clk and price
        self.train_clicks_prices = []  # clk and price
        self.pctrs = []  # pCTR from logistic regression prediction
        self.total_cost = 0  # total original cost during the test data
        self.read_train_data(train_data)
        self.read_test_data(test_data)
        self.read_pctr(pctr_data)
        self.name = name

    def read_train_data(self, input_file):
        # read in train data for original_ecpc and original_ctr
        fi = open(input_file, 'r')
        first = True
        imp_num = 0
        for line in fi:
            s = line.split(' ')
            if first:
                first = False
                continue
            click = int(s[0])
            cost = int(s[1])
            imp_num += 1
            self.original_ctr += click
            self.original_ecpc += cost
            self.train_clicks_prices.append((click, cost))
        fi.close()
        self.original_ecpc /= self.original_ctr
        self.original_ctr /= imp_num

    def read_test_data(self, input_file):
        # read in test data
        fi = open(input_file, 'r')
        for line in fi:
            s = line.split(' ')
            click = int(s[0])
            winning_price = int(s[1])
            self.test_clicks_prices.append((click, winning_price))
            self.total_cost += winning_price
        fi.close()

    def read_pctr(self, input_file):
        # read in pctr from logistic regression
        fi = open(input_file, 'r')
        for line in fi:
            self.pctrs.append(float(line.strip()))
        fi.close()


class BaseStrategy(object):
    name = ''

    def __init__(self, proportion, para, campaign):
        self.cost = 0
        self.clks = 0
        self.bids = 0
        self.imps = 0
        self.ecpc = None
        self.budget = int(campaign.total_cost / proportion)  # initialise the budget
        self.proportion = proportion
        self.para = para
        self.campaign = campaign

    def simulate(self):
        for idx in range(0, len(self.campaign.clicks_prices)):
            pctr = self.campaign.pctrs[idx]
            bid = self.bid(pctr)
            self.bids += 1
            case = self.campaign.clicks_prices[idx]
            if self.win_auction(case[1], bid):
                self.imps += 1
                self.clks += case[0]
                self.cost += case[1]
                if self.clks:
                    self.ecpc = self.cost / self.clks
            if self.cost > self.budget:
                break

    def performance(self):
        return self.ecpc + self.ecpc * abs(self.cost - self.budget) / self.budget

    def results(self):
        return str(self.proportion) + '\t' + str(self.clks) + '\t' + str(self.bids) + '\t' + \
               str(self.imps) + '\t' + str(self.budget) + '\t' + str(self.cost) + '\t' + self.name + '\t' + str(
            self.para)

    def win_auction(self, winning_price, bid):
        return bid > winning_price

    def bid(self, pctr):
        raise NotImplemented


class LinearBiddingStrategy(BaseStrategy):
    name = 'lin'

    def bid(self, pctr):
        return int(pctr * self.para / self.campaign.original_ctr)


class CPCBiddingStrategy(BaseStrategy):
    name = 'mcpc'

    def __init__(self, proportion, para, campaign):
        BaseStrategy.__init__(self, proportion, para, campaign)
        self.targetcpc = self.get_targetcpc()
        self.para = self.targetcpc

    def get_targetcpc(self):
        raise NotImplemented

    def bid(self, pctr):
        return int(self.targetcpc * pctr)


class CPCFixedBiddingStrategy(CPCBiddingStrategy):
    name = 'cpc lin'

    def get_targetcpc(self):
        """
        reading ecpc from linear form bidding
        :return:
        """
        fi = open(os.path.join(results_dir, 'rtb.results.%s.best.perf.tsv' % self.campaign.name), 'r')
        first = True
        ecpc = 0
        for line in fi:
            line = line.strip()
            s = line.split('\t')
            if first:
                first = False
                continue
            algo = s[6]
            prop = s[0]
            if str(self.proportion) == prop and algo == 'lin':
                ecpc = float(s[5]) / float(s[1])
        fi.close()
        return ecpc


class CPCComputedBiddingStrategy(CPCBiddingStrategy):
    name = 'aggressive'

    def get_targetcpc(self):
        # for each record in period, compute cpc
        cpcs = []
        for idx in range(0, len(self.campaign.clicks_prices)):
            pctr = self.campaign.pctrs[idx]
            case = self.campaign.clicks_prices[idx]
            cost = case[1]
            cpc = cost / pctr
            cpcs.append((cpc, cost))

        cpcs.sort()

        costs = 0
        prev_cpc = 0
        for cpc, cost in cpcs:
            costs += cost
            if costs > self.budget:
                return prev_cpc
            prev_cpc = cpc
        return 1000000


class CPCAggresivenessBiddingStrategy(CPCComputedBiddingStrategy, CPCFixedBiddingStrategy):
    name = 'experiment 1'

    def get_targetcpc(self):
        lin_ecpc = CPCFixedBiddingStrategy.get_targetcpc(self)
        aggressive_ecpc = CPCComputedBiddingStrategy.get_targetcpc(self)
        difference = aggressive_ecpc - lin_ecpc
        return lin_ecpc + difference * self.para


class CPCBid(CPCBiddingStrategy):
    name = 'experiment'

    def get_targetcpc(self):

        impression_log = self.campaign.train_clicks_prices
        n_impression_log = len(impression_log)

        click_log = [c[1] for c in impression_log if c[0]]
        n_click_log = len(click_log)

        n_test_click = n_click_log/2  # train/test split

        ctr_train = int(n_impression_log / n_click_log)

        # price distribution for clicks
        KDEpdf = scipy.stats.gaussian_kde(click_log)

        cost_of_clicks = scipy.integrate.quad(lambda x: x*n_test_click * KDEpdf(x)[0], 0, np.inf)
        # print(cost_of_clicks[0])

        expected_costs = cost_of_clicks[0] * ctr_train
        # print(expected_costs)

        target_cpc = 0
        costs = 0

        if expected_costs > self.budget and True:
            while costs < self.budget:
                result = scipy.integrate.quad(lambda x: ctr_train * x * n_test_click * KDEpdf(x)[0], 0, target_cpc)
                costs = result[0]
                target_cpc += 1
        else:
            print('Can not spend all budget like this')

        return int(costs/target_cpc)


class CPCPerfectBid(CPCBiddingStrategy):
    name = 'perfect'

    def get_targetcpc(self):

        impression_log = self.campaign.clicks_prices
        n_impression_log = len(impression_log)

        click_log = [c[1] for c in impression_log if c[0]]
        n_click_log = len(click_log)

        n_test_click = n_click_log  # train/test split

        ctr_train = int(n_impression_log / n_click_log)

        # price distribution for clicks
        KDEpdf = scipy.stats.gaussian_kde(click_log)

        cost_of_clicks = scipy.integrate.quad(lambda x: x*n_test_click * KDEpdf(x)[0], 0, np.inf)
        # print(cost_of_clicks[0])

        expected_costs = cost_of_clicks[0] * ctr_train
        # print(expected_costs)

        target_cpc = 0
        costs = 0

        if expected_costs > self.budget and True:
            while costs < self.budget:
                result = scipy.integrate.quad(lambda x: ctr_train * x * n_test_click * KDEpdf(x)[0], 0, target_cpc)
                costs = result[0]
                target_cpc += 1
        else:
            print('Can not spend all budget like this')

        return int(costs/target_cpc)
