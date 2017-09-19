from strategies import *

results = os.path.join(results_dir, "analysis")
if not os.path.exists(results):
    os.makedirs(results)

for campaign_name in campaigns:
    campaign_log_folder = os.path.join(logfolder, campaign_name)
    campaign = Campaign(campaign_name, os.path.join(campaign_log_folder, 'train.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt'),
                        os.path.join(campaign_log_folder, 'test.yzx.txt.lr.pred'))

    # parameters setting for each bidding strategy
    mcpc_paras = [1]
    mcpc_exp_paras = [x / 10.0 for x in range(1, 10, 1)]

    algo_paras = {"mcpc_lin": mcpc_paras, "aggressive": mcpc_paras, "mcpc_exp": mcpc_exp_paras}

    fo = open(os.path.join(results, 'rtb.results.%s.tsv' % campaign_name), 'w')
    header = "prop\tclks\tbids\timps\tbudget\tspend\talgo\tpara"
    fo.write(header + "\n")
    print(header)
    for proportion in budget_proportions:
        for algo in algo_paras:
            paras = algo_paras[algo]
            for para in paras:
                if False:
                    pass
                elif algo == "mcpc_lin":
                    strategy = CPCFixedBiddingStrategy(proportion, para, campaign)
                elif algo == "aggressive":
                    strategy = CPCComputedBiddingStrategy(proportion, para, campaign)
                # elif algo == "mcpc_exp":
                #     strategy = CPCAggresivenessBiddingStrategy(proportion, para, campaign)
                else:
                    break
                strategy.simulate()
                print(strategy.results())
                fo.write(strategy.results() + '\n')
    fo.close()
