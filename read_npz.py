# Requirement: [pip install numpy]

import numpy as np

read = np.load("training_data.npz")
# print(read.files)  # Uncomment to view the keys ['q_table', 'epsilon']
print(f"Q-Tables: {read['q_table']}\n")
print(f"Epsilon: {read['epsilon']}")
