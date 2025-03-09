# Pandas DataFrame Cheatsheet

## 1. Creation

- **From a dictionary or list of dictionaries:**

  ```python
  import pandas as pd

  data = {
      'A': [1, 2, 3],
      'B': [4, 5, 6]
  }
  df = pd.DataFrame(data)
  ```

- **From a list of lists (with columns specified):**

  ```python
  data = [
      [1, 4],
      [2, 5],
      [3, 6]
  ]
  df = pd.DataFrame(data, columns=['A', 'B'])
  ```

---

## 2. Inspecting Data

- **Preview data:**
  - `df.head(n)` – First *n* rows (default is 5).
  - `df.tail(n)` – Last *n* rows.

- **Summary:**
  - `df.info()` – Data types and non-null counts.
  - `df.describe()` – Statistical summary of numeric columns.
  - `df.shape` – Tuple of (rows, columns).
  - `df.columns` – List of column names.
  - `df.index` – Row index.

---

## 3. Indexing & Selecting Data

- **Column selection:**
  - Single column: `df['column']` or `df.column`
  - Multiple columns: `df[['col1', 'col2']]`

- **Row selection:**
  - **Label-based:** `df.loc[row_label, col_label]`
  - **Position-based:** `df.iloc[row_index, col_index]`

- **Scalar access (fast):**
  - `df.at[row_label, 'column']`
  - `df.iat[row_index, col_index]`

- **Conditional selection:**

  ```python
  df_filtered = df[df['A'] > 2]
  ```

---

## 4. DataFrame Operations

- **Sorting:**
  - By column: `df.sort_values(by='column', ascending=True)`
  - By index: `df.sort_index()`

- **Applying functions:**
  - **Element-wise:** `df.applymap(lambda x: x * 2)`
  - **Column/Row-wise:** `df.apply(np.sum, axis=0)`  *(axis=0 for columns, axis=1 for rows)*

- **Transposing:**
  - `df.T`

---

## 5. Modifying Data

- **Adding or modifying columns:**

  ```python
  df['C'] = df['A'] + df['B']
  ```

- **Renaming columns:**

  ```python
  df.rename(columns={'A': 'Alpha', 'B': 'Beta'}, inplace=True)
  ```

- **Dropping columns or rows:**

  ```python
  df.drop(columns=['Beta'], inplace=True)
  df.drop(index=[0], inplace=True)
  ```

---

## 6. Handling Missing Data

- **Detection:**
  - `df.isna()`
  - `df.notna()`

- **Removal:**
  - `df.dropna()` – Remove rows with missing values.
  - `df.dropna(axis=1)` – Remove columns with missing values.

- **Filling missing values:**

  ```python
  df.fillna(0, inplace=True)
  ```

---

## 7. Grouping & Aggregation

- **Grouping:**

  ```python
  grouped = df.groupby('column')
  grouped.mean()  # Compute mean for each group
  ```

- **Aggregation:**
  - Multiple aggregations: `df.groupby('column').agg({'A': 'sum', 'B': 'mean'})`

---

## 8. Merging & Joining

- **Concatenation:**

  ```python
  df_new = pd.concat([df1, df2], axis=0)  # Stacking rows
  ```

- **Merge/Join:**

  ```python
  df_merged = pd.merge(df1, df2, on='common_column', how='inner')
  ```

---

## 9. Pivoting & Reshaping

- **Pivoting:**

  ```python
  pivot_df = df.pivot(index='date', columns='category', values='value')
  ```

- **Melting (unpivoting):**

  ```python
  melted_df = pd.melt(df, id_vars=['id'], value_vars=['col1', 'col2'])
  ```

- **Stack/Unstack:**

  ```python
  stacked = df.stack()    # Convert columns to rows
  unstacked = stacked.unstack()  # Convert back to DataFrame
  ```

---

## 10. I/O Operations

- **Reading from files:**

  ```python
  df_csv = pd.read_csv('file.csv')
  df_excel = pd.read_excel('file.xlsx')
  ```

- **Writing to files:**

  ```python
  df.to_csv('output.csv', index=False)
  df.to_excel('output.xlsx', index=False)
  ```

---

## 11. Miscellaneous

- **Copying DataFrames:**

  ```python
  df_copy = df.copy()
  ```

- **Memory usage:**

  ```python
  df.memory_usage(deep=True)
  ```

- **Iterating over rows (less efficient):**

  ```python
  for index, row in df.iterrows():
      print(index, row['A'])
  ```

- **Vectorized operations are preferred for performance.**
