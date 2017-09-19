from settings import *

sub_results = ['analysis', 'cpcbid']

all_results = os.path.join(results_dir, "all")
if not os.path.exists(all_results):
    os.makedirs(all_results)

for campaign in campaigns:
    original_results = os.path.join(results_dir, 'rtb.results.%s.best.perf.tsv' % campaign)
    with open(os.path.join(all_results, '%s.tsv' % campaign), 'w') as outfile:
        with open(original_results) as infile:
            for line in infile:
                outfile.write(line)
        for fname in sub_results:
            with open(os.path.join(results_dir, fname, 'rtb.results.%s.tsv' % campaign)) as infile:
                first = True
                for line in infile:
                    if not first:
                        outfile.write(line)
                    else:
                        first = False

