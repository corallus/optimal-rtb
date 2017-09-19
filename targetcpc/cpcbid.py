from strategies import *

results = os.path.join(results_dir, "cpcbid")
if not os.path.exists(results):
    os.makedirs(results)

for campaign_name in campaigns:
    campaign_log_folder = os.path.join(logfolder, campaign_name)
    campaign = Campaign(campaign_name, os.path.join(campaign_log_folder, 'train.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt.lr.pred'))

    fo = open(os.path.join(results, 'rtb.results.%s.tsv' % campaign_name), 'w')
    header = "prop\tclks\tbids\timps\tbudget\tspend\talgo\tpara"
    fo.write(header + "\n")
    print(header)
    for proportion in budget_proportions:
        strategy = CPCBid(proportion, 1, campaign)
        strategy.simulate()
        print(strategy.results())
        fo.write(strategy.results() + '\n')
        strategy = CPCPerfectBid(proportion, 1, campaign)
        strategy.simulate()
        print(strategy.results())
        fo.write(strategy.results() + '\n')
    fo.close()
