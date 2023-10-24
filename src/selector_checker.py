from z3 import *
import random
import time
import tempfile
from multiprocessing import Process, Queue
import pandas as pd

filename_1 = ""
filename_2 = ""

def load_declarations(filename):
    with open(filename, 'r') as f:
        return f.read()

def load_axioms(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]
    
def solver_task(temp_filename, queue):
    s = Solver()
    s.from_file(temp_filename)
    result = s.check()
    queue.put(result)

def check_with_timeout(declarations, axioms, timeout):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.smt2') as temp:
        temp.write(declarations)
        temp.write("\n")
        temp.write(axioms)
        temp_filename = temp.name

    queue = Queue()
    process = Process(target=solver_task, args=(temp_filename, queue))
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        process.terminate()
        return "timeout"
    else:
        return queue.get()

def main():
    declarations = load_declarations(filename_1)
    all_axioms = load_axioms(filename_2)

    num_iterations = int(input("Enter the number of iterations: "))

    unsat_subsets = []
    timeout_subsets = []

    for _ in range(num_iterations):
        selected_axioms = "\n".join(random.sample(all_axioms, 7))

        result = check_with_timeout(declarations, selected_axioms, 30)
        if result == sat:
            print("sat")
        elif result == unsat:
            unsat_subsets.append(selected_axioms)
            print("unsat")
        elif result == "timeout":
            timeout_subsets.append(selected_axioms)
            print("timeout")

    if unsat_subsets:
        df_unsat = pd.DataFrame({'Unsat Axiom Subsets': unsat_subsets})
        df_unsat.to_csv('unsat_subsets.csv', index=False)


    # Display timeout subsets in a table
    if timeout_subsets:
        df_timeout = pd.DataFrame({'Timeout Axiom Subsets': timeout_subsets})
        df_timeout.to_csv('timeout_subsets.csv', index=False)
        
if __name__ == "__main__":
    main()
