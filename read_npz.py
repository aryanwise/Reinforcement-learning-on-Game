"""
Python script to print the Q_table and Epsilon Values using Numpy from the training_data.npz
"""

# Requirement: [pip install numpy]

import numpy as np

read = np.load("training_data.npz")
# print(read.files)  # Uncomment to view the keys ['q_table', 'epsilon']
print(f"{'='*100}\nQ-Tables: \n{read['q_table']}\n")
print(f"{'='*100}\nEpsilon: {read['epsilon']}\n{'='*100}")
