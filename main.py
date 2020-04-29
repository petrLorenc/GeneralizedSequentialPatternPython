import logging
import multiprocessing as mp

logging.basicConfig(level=logging.DEBUG)


class GSP:

    def __init__(self, transactions, minsup):
        self.transactions = transactions
        self.max_size = max([len(item) for item in transactions])
        self.freq_patterns = []
        self.minsup = minsup
        assert (0.0 < self.minsup) and (self.minsup <= 1.0)

    def _is_slice_in_list(self, s, l, w):
        """

        :param s: slice we are looking for
        :param l: list where we are looking
        :param w: windows where to look for patterns
        :return: true/false
        """
        assert (w >= 0)

        len_s = len(s)  # so we don't recompute length of s on every iteration
        o = []
        for idx_l in range(len(l) - len_s + 1):
            is_slice_in_list = True
            for idx_s in range(len_s):
                if type(l[idx_l + idx_s]) == frozenset:
                    if s[idx_s] not in l[idx_l + idx_s]:
                        if w == 0:
                            is_slice_in_list = False
                            break
                        else:
                            w -= 1
                else:
                    if s[idx_s] is not l[idx_l + idx_s]:
                        if w == 0:
                            is_slice_in_list = False
                            break
                        else:
                            w -= 1
            o.append(is_slice_in_list)

        return any(o)

    def _calc_frequency(self, results, item, minsup, window):
        # The number of times the item appears in the transactions
        frequency = len(
            [t for t in self.transactions if self._is_slice_in_list(item, t, window)])
        if frequency >= minsup:
            results[tuple(item)] = frequency
        return results

    def _support(self, items, minsup=0.0, window=0):
        '''
        The support count (or simply support) for a sequence is defined as
        the fraction of total data-sequences that "contain" this sequence.
        (Although the word "contains" is not strictly accurate once we
        incorporate taxonomies, it captures the spirt of when a data-sequence
        contributes to the support of a sequential pattern.)

        Parameters
                items: set of items that will be evaluated
                minsup: minimum support
                window: TODO implement
        '''
        results = mp.Manager().dict()
        pool = mp.Pool(processes=mp.cpu_count())

        for item in items:
            pool.apply_async(self._calc_frequency,
                             args=(results, item, minsup, window))
        pool.close()
        pool.join()

        return dict(results)

    def _generate_candidates(self):
        o = []
        for l in self.transactions:
            for x in l:
                if type(x) is frozenset:
                    for xx in x:
                        o.append(xx)
                else:
                    o.append(x)
        return list(set(tuple(o)))

    def _do_product(self, items):
        """
        Combining the two tuples based on GSP alg - remove the first and last item
        and then try to match the rest together
        for example (a, b, c) and (b, c, e) create (a, b, c, e)
        :param items:
        :return:
        """
        new_candidates = []
        if max([len(i) for i in items]) == 1:
            for x in items:
                for y in items:
                    new_candidates.append((x[0], y[0]))
        else:
            mapping_rest_to_first = {i[1:]: i[0] for i in items}
            mapping_rest_to_last = {i[:-1]: i[-1] for i in items}

            for k, v in mapping_rest_to_first.items():
                if k in mapping_rest_to_last:
                    new_candidates.append(tuple(mapping_rest_to_first[k]) + k + tuple(mapping_rest_to_last[k]))

        return list(set(new_candidates))

    def run_alg(self):
        minsup = len(transactions) * self.minsup

        # Initially, every item in DB is a candidate
        candidates = self._generate_candidates()

        # Scan transactions to collect support count for each candidate
        self.freq_patterns.append(self._support(candidates, minsup))

        # Iterations counter
        k_items = 1

        # repeat until no frequent sequence or no candidate can be found
        while len(self.freq_patterns[k_items - 1]) and (k_items + 1 <= self.max_size):
            k_items += 1

            # Generate candidate sets Ck (set of candidate k-sequences) -
            # generate new candidates from the last "best" candidates filtered
            # by minimum support
            items = list(set(self.freq_patterns[k_items - 2].keys()))
            candidates = list(self._do_product(items))

            # Candidate pruning - eliminates candidates who are not potentially
            # frequent (using support as threshold)
            self.freq_patterns.append(self._support(candidates, minsup))

        return self.freq_patterns[-2]


if __name__ == '__main__':
    transactions = [["a", "b", "c", frozenset(["c", "d"]), "d"], ["a", "a", "b", frozenset(["c", "d"])], ["a", "a"]]

    alg = GSP(transactions=transactions,  minsup=0.1)
    print(alg.run_alg())
