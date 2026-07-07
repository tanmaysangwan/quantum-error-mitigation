import numpy as np

ideal_result = 1.0

noisy_results = np.array([
    0.82,
    0.79,
    0.85,
    0.81,
    0.83
])

weights = np.array([
    1.2,
    -0.3,
    0.8,
    -0.7,
    0.2
])

pec_estimate = np.sum(noisy_results * weights)

print("Ideal Result:")
print(ideal_result)

print("\nNoisy Results:")
print(noisy_results)

print("\nWeights:")
print(weights)

print("\nWeighted Results:")
print(noisy_results * weights)

print("\nPEC Estimate:")
print(pec_estimate)

print("\nAbsolute Error:")
print(abs(ideal_result - pec_estimate))