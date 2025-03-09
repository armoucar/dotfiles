Below is a concise cheatsheet for working with **pandas.core.series.Series**. This guide covers common operations, methods, and usage patterns when working with Series in pandas.

---

# Pandas Series Cheatsheet

## 1. Creation

- **From a list or array:**

  ```python
  import pandas as pd
  import numpy as np

  data = [10, 20, 30, 40]
  s = pd.Series(data)
  ```

- **From a dictionary (with keys as index labels):**

  ```python
  data = {'a': 1, 'b': 2, 'c': 3}
  s = pd.Series(data)
  ```

- **With a custom index:**

  ```python
  data = [100, 200, 300]
  s = pd.Series(data, index=['x', 'y', 'z'])
  ```

---

## 2. Inspecting Data

- **Previewing values:**
  - `s.head(n)` – First *n* elements (default is 5).
  - `s.tail(n)` – Last *n* elements.

- **Summary:**
  - `s.describe()` – Statistical summary (count, mean, std, etc.).
  - `s.shape` – Tuple indicating number of elements.
  - `s.index` – Index labels.
  - `s.dtype` – Data type of the Series.

---

## 3. Indexing & Selecting Data

- **Accessing elements by label or position:**
  - Label-based: `s.loc['a']`
  - Position-based: `s.iloc[0]`

- **Slicing:**

  ```python
  # Slicing by position
  s.iloc[1:3]

  # Slicing by label (if index is sorted)
  s.loc['a':'c']
  ```

- **Conditional selection:**

  ```python
  s_filtered = s[s > 20]
  ```

---

## 4. Arithmetic & Vectorized Operations

- **Element-wise operations:**

  ```python
  s2 = s + 5        # Add 5 to every element
  s3 = s * 2        # Multiply every element by 2
  ```

- **Using NumPy functions:**

  ```python
  np.sqrt(s)
  ```

- **Aggregation methods:**
  - `s.sum()`
  - `s.mean()`
  - `s.median()`
  - `s.std()`

---

## 5. Handling Missing Data

- **Detection:**
  - `s.isna()` or `s.isnull()`
  - `s.notna()` or `s.notnull()`

- **Removal:**
  - `s.dropna()`

- **Filling missing values:**

  ```python
  s_filled = s.fillna(0)
  ```

---

## 6. String Operations

- **For Series of strings, use the `.str` accessor:**

  ```python
  s_str = pd.Series(['Apple', 'Banana', 'Cherry'])
  s_lower = s_str.str.lower()            # Convert to lowercase
  contains_a = s_str.str.contains('a')     # Boolean mask for presence of 'a'
  ```

---

## 7. Date/Time Operations

- **Converting to datetime:**

  ```python
  dates = pd.Series(['2025-01-01', '2025-01-02', '2025-01-03'])
  dates = pd.to_datetime(dates)
  ```

- **Using the `.dt` accessor:**

  ```python
  day = dates.dt.day
  month = dates.dt.month
  weekday = dates.dt.weekday
  ```

---

## 8. Sorting & Ranking

- **Sorting:**
  - By value: `s.sort_values()`
  - By index: `s.sort_index()`

- **Ranking:**

  ```python
  ranks = s.rank()
  ```

---

## 9. Plotting

- **Basic plotting (requires matplotlib):**

  ```python
  import matplotlib.pyplot as plt

  s.plot(kind='line')  # Other options: 'bar', 'hist', etc.
  plt.show()
  ```

---

## 10. Miscellaneous

- **Unique values and frequency:**
  - `s.unique()` – Array of unique elements.
  - `s.value_counts()` – Count occurrences of each value.

- **Conversion:**
  - To list: `s.tolist()`
  - To NumPy array: `s.values` or `s.to_numpy()`

- **Copying a Series:**

  ```python
  s_copy = s.copy()
  ```

---

This cheatsheet offers a quick reference to the most common operations and methods available for pandas Series. Experiment with these commands in your projects to deepen your understanding of pandas.
