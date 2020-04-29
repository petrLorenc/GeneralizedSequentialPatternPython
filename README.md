# Generalized Sequence Pattern (GSP) algorithm in Python

[Inspiration for code](https://github.com/jacksonpradolima/gsp-py)

[Inspiration for algorithm](http://simpledatamining.blogspot.com/2015/03/generalized-sequential-pattern-gsp.html)

# Features

Support frozenset as an item (this gives us a possibility to express close relation between items - for example, that they were bought together).
The algorithm will also search for sequences where one item from frozen set is present. For more detail look at links above. 

# Usage

    
    transactions = [["a", "b", "c", frozenset(["c", "d"]), "d"], 
                    ["a", "a", "b", frozenset(["c", "d"])], ["a", "a"]]

    alg = GSP(transactions=transactions,  minsup=0.1)
    print(alg.run_alg())
    # return {('a', 'b', 'c', 'c'): 1}
    
# Not implemented

 * Search window