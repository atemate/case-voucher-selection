# Jupyter notebooks

## clean_data.ipynb: EDA and data cleaning
This notebook explores the schema of the given raw data and creates a new dataset [../data/data_cleaned.csv](../data/data_cleaned.csv) of the same schema as the original parquet file:

```
$ head -n1 data/data_cleaned.csv
,timestamp,country_code,last_order_ts,first_order_ts,total_orders,voucher_amount
```

The following transformations are applied:
- Check the timestamps are not null and convertible to `datetime`.
- Fix the column `total_orders`:
    - use value `0.0` instead of empty strings
    - convert all values to `int`
- Fix the column `voucher_amount`:
    - use value `0` instead of NaN
    - convert all values to `int`
