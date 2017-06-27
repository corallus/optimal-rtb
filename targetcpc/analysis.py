from __future__ import division
import matplotlib.pyplot as plt

from settings import *
from strategies import Campaign

output_dir = os.path.join(figures_dir, 'analysis')


class Plot:
    def __init__(self, camps, algos, ylabel, attribute, output_file):
        self.camps = camps
        self.algos = algos
        self.attribute = attribute
        plt.figure(ylabel)
        plt.ylabel(ylabel)
        self.plot(output_file)

    @staticmethod
    def get_x_values():
        plt.xlabel('Budget proportion')
        return [1/budget for budget in budget_proportions]

    def get_y_values(self, algo):
        list = []
        for prop in budget_proportions:
            aggr = 0
            for camp in self.camps:
                aggr += self.read_prop(camp, algo, prop, self.attribute)
            list.append(aggr)
        return list

    def infile(self, campaign):
        return os.path.join(results_dir, 'all', '%s.tsv' % campaign)

    def plot(self, output_file):
        for algo in self.algos:
            self.get_y_values(algo)
            plt.plot(self.get_x_values(), self.get_y_values(algo))
        plt.legend(self.algos, loc='upper left')
        if output_file:
            plt.savefig(os.path.join(output_dir, output_file))
            plt.close()
        else:
            plt.show()

    def read_prop(self, campaign, algorithm, proportion, index):
        fi = open(self.infile(campaign), 'r')
        first = True
        for line in fi:
            line = line.strip()
            s = line.split('\t')
            if first:
                first = False
                continue
            if s[6] == algorithm and s[0] == str(proportion):
                return int(s[index])
        fi.close()


class PlotECPC(Plot):
    def get_y_values(self, algo):
        plt.ylabel('eCPC')
        list = []
        for prop in budget_proportions:
            costs = 0
            clicks = 0
            for camp in self.camps:
                clicks += self.read_prop(camp, algo, prop, 1)
                costs += self.read_prop(camp, algo, prop, 5)
            list.append(costs/clicks)
        return list


class PlotPerformance(Plot):
    def get_y_values(self, algo):
        plt.ylabel('ecpc + ecpc * abs(costs - budget) / budget')
        list = []
        for prop in budget_proportions:
            costs = 0
            clicks = 0
            budget = 0
            for camp in self.camps:
                budget += self.read_prop(camp, algo, prop, 4)
                clicks += self.read_prop(camp, algo, prop, 1)
                costs += self.read_prop(camp, algo, prop, 5)
            ecpc = costs/clicks
            performance = ecpc + ecpc * abs(costs - budget) / budget
            list.append(performance)
        return list


class PlotBudgetSpend(Plot):
    def get_y_values(self, algo):
        plt.ylabel('% of budget spent')
        list = []
        for prop in budget_proportions:
            costs = 0
            budget = 0
            for camp in self.camps:
                budget += self.read_prop(camp, algo, prop, 4)
                costs += self.read_prop(camp, algo, prop, 5)
            list.append(100*costs/budget)
        return list

algos = ['lin', 'mcpc', 'cpc lin', 'aggressive']

Plot(campaigns, algos, "Clicks", 1, 'clicks.png')

Plot(campaigns, algos, "Costs", 5, 'costs.png')

PlotECPC(campaigns, algos, "eCPC", 5, 'ecpc.png')
for c in campaigns:
    PlotECPC([c], algos, "eCPC %s" % c, 5, 'ecpc_%s.png' % c)

PlotPerformance(campaigns, algos, "ecpc + ecpc * abs(costs - budget) / budget", 5, 'performance.png')
for c in campaigns:
    PlotPerformance([c], algos, "%s" % c, 5, 'performance_%s.png' % c)

PlotBudgetSpend(campaigns, algos, "Budget spent", 5, 'budget_spent.png')

"""
for campaign_name in campaigns:
    campaign_log_folder = os.path.join(logfolder, campaign_name)
    campaign = Campaign(campaign_name, os.path.join(campaign_log_folder, 'train.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt.lr.pred'))

    ecpcs = [case[1]/case[0] for case in campaign.clicks_prices if case[0]]
    from sklearn.linear_model import LogisticRegression
    import numpy as np

    prices = [case[1] for case in campaign.clicks_prices]
    prices = np.array(prices).reshape(-1, 1)
    clicks = [case[0] for case in campaign.clicks_prices]
    clicks = np.array(clicks).reshape(-1, 1)

    model = LogisticRegression()
    model.fit(prices, clicks)
    plt.plot(prices, model.predict_proba(prices)[:, 1], color="r")
    plt.show()
"""