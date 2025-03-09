## Pandas Cheatsheet

### **1. Data Ingestion & Export**
```python
import pandas as pd

# Reading data
df = pd.read_csv('data.csv')
df_excel = pd.read_excel('data.xlsx')

# Writing data
df.to_csv('output.csv', index=False)
df.to_excel('output.xlsx', index=False)
```

### **2. DataFrame Basics**
```python
# Displaying data
df.head()         # First 5 rows
df.tail()         # Last 5 rows
df.info()         # DataFrame info (types, non-null counts)
df.describe()     # Summary statistics
```

### **3. Indexing and Slicing**
```python
# Selecting columns
df['column_name']
df[['col1', 'col2']]

# Using loc and iloc
df.loc[0, 'column_name']    # Label based
df.iloc[0, 0]               # Position based

# Boolean indexing
filtered_df = df[df['sales'] > 1000]
```

### **4. Data Cleaning**
```python
# Handling missing values
df.dropna()               # Drop rows with missing values
df.fillna(value=0)        # Replace missing values with 0

# Renaming columns
df.rename(columns={'old_name': 'new_name'}, inplace=True)

# Converting data types
df['date'] = pd.to_datetime(df['date'])
```

### **5. Aggregation & Grouping**
```python
# Grouping and aggregating
grouped = df.groupby('category').agg({'sales': 'sum', 'profit': 'mean'})
grouped.reset_index()     # Convert grouped index back to a column

# Pivot table
pivot = df.pivot_table(index='region', values='sales', aggfunc='sum')
```

### **6. Merging and Joining**
```python
# Merging DataFrames
merged_df = pd.merge(df1, df2, on='key_column', how='inner')

# Concatenating DataFrames
combined_df = pd.concat([df1, df2], ignore_index=True)
```

### **7. Data Transformation**
```python
# Applying functions and lambda operations
df['new_column'] = df['sales'].apply(lambda x: x * 1.1)

# Using vectorized operations
df['adjusted_sales'] = df['sales'] * 1.1
```

### **8. Sorting and Filtering**
```python
# Sorting
df.sort_values('sales', ascending=False, inplace=True)

# Filtering with multiple conditions
filtered_df = df[(df['sales'] > 1000) & (df['profit'] > 100)]
```

### **9. Basic Visualization**
```python
import matplotlib.pyplot as plt

# Quick line plot
df['sales'].plot(title='Sales Trend')
plt.show()

# Bar plot
df.groupby('category')['sales'].sum().plot(kind='bar', title='Sales by Category')
plt.show()
```

---

### **Final Tips**
- **Practice with Real Data:** The best learning comes from tackling real datasets.
- **Use the Documentation:** Keep the [Pandas documentation](https://pandas.pydata.org/docs/) handy as a reference.
- **Write Readable Code:** Favor method chaining and clear variable names.
- **Focus on Efficiency:** Leverage vectorized operations instead of looping over rows.

This plan and cheatsheet provide a focused roadmap to ramp up quickly with the most impactful Pandas functionality for business analytics and data manipulation tasks. Enjoy your learning journey!
