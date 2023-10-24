from z3 import *
import random
import time
import tempfile
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

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

def generate_voronoi(points, axioms_list, times_list):
    vor = Voronoi(points)
    fig, ax = plt.subplots()
    voronoi_plot_2d(vor, ax=ax)

    for i, (x, y) in enumerate(points):
        ax.annotate(f"Axioms: {axioms_list[i]}\nTime: {times_list[i]}", (x, y), visible=False)

    def on_hover(event):
        if event.xdata is None or event.ydata is None:
            return
        for annotation in ax.get_children():
            if isinstance(annotation, plt.Annotation):
                annotation.set_visible(False)
        for i, (x, y) in enumerate(points):
            if abs(event.xdata - x) < 0.5 and abs(event.ydata - y) < 0.5:
                ax.get_children()[i].set_visible(True)
        plt.draw()

    fig.canvas.mpl_connect('motion_notify_event', on_hover)
    plt.show()

def main():
    declarations = load_declarations(filename_1)
    all_axioms = load_axioms(filename_2)

    num_subsets = int(input("Enter the number of subsets: "))
    partition_size = int(input("Enter the size of partitions: "))

    points = []
    axioms_list = []
    times_list = []

    for _ in range(num_subsets):
        selected_axioms = "\n".join(random.sample(all_axioms, partition_size))
        start_time = time.time()
        result = check_with_timeout(declarations, selected_axioms, 30)
        elapsed_time = time.time() - start_time

        x, y = random.uniform(0, 100), random.uniform(0, 100)  # Generate random coordinates for the point
        points.append((x, y))
        axioms_list.append(selected_axioms)
        times_list.append(elapsed_time)

    generate_voronoi(points, axioms_list, times_list)

if __name__ == "__main__":
    main()
