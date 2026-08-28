"""
Skew Demo Script — Spark Standalone Cluster (docker-compose)
Cluster: 2 workers x 2 cores x 2G RAM = 4 cores, 4G total

Run:
  docker exec -it spark-client /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.cores=2 \
    --conf spark.executor.memory=1500m \
    /opt/spark-apps/skew_demo.py
"""

from pyspark.sql import SparkSession, functions as F
import random

# ---------------------------------------------------------
# Step 0: SparkSession — master() 
# spark-submit ke --master flag 
# ---------------------------------------------------------
spark = SparkSession.builder \
    .appName("ShuffleSkewScenario") \
    .config("spark.sql.shuffle.partitions", "10") \
    .config("spark.sql.adaptive.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")  

print("\n[INFO] SparkSession created. UI available at http://localhost:4040\n")

# ---------------------------------------------------------
# Step 1: Orders table (INTENTIONALLY SKEWED)
# R1 (Lahore) = 85% of all rows -> hot key
# ---------------------------------------------------------
orders_data = []
for i in range(5_000_000):
    if random.random() < 0.85:
        region = "R1"
    else:
        region = f"R{random.randint(2, 6)}"
    orders_data.append((i, region, random.randint(100, 5000)))

orders_df = spark.createDataFrame(orders_data, ["order_id", "region_id", "amount"])

# ---------------------------------------------------------
# Step 2: Region master (small dimension table -> auto broadcast)
# ---------------------------------------------------------
region_master_df = spark.createDataFrame(
    [("R1", "Lahore"), ("R2", "Karachi"), ("R3", "Islamabad"),
     ("R4", "Multan"), ("R5", "Peshawar"), ("R6", "Quetta")],
    ["region_id", "region_name"]
)

# ---------------------------------------------------------
# Step 3: JOIN + cache 
# ---------------------------------------------------------
joined_df = orders_df.join(region_master_df, on="region_id", how="inner").cache()
joined_df.count()  

print("[INFO] joined_df cached. \n")

# ---------------------------------------------------------
# Step 4: Aggregation (GROUPBY -> shuffle skew)
# ---------------------------------------------------------
print("[INFO] Running groupBy aggregation...")
result_df = joined_df.groupBy("region_id", "region_name") \
    .agg(F.count("*").alias("total_orders"), F.sum("amount").alias("total_amount"))

result_df.orderBy(F.desc("total_orders")).show(truncate=False)

# ---------------------------------------------------------
# Step 5: Partition-level physical skew check (post-shuffle)
# ---------------------------------------------------------
print("[INFO] Checking shuffle partition sizes AFTER groupBy shuffle...")

joined_df.groupBy("region_id", "region_name") \
    .agg(F.count("*").alias("total_orders"), F.sum("amount").alias("total_amount")) \
    .withColumn("part_id", F.spark_partition_id()) \
    .groupBy("part_id") \
    .agg(F.sum("total_orders").alias("rows_in_partition")) \
    .orderBy(F.desc("rows_in_partition")) \
    .show(20, truncate=False)

# ---------------------------------------------------------
# Step 6: Numeric skew proof
# ---------------------------------------------------------
print("[INFO] Numeric skew summary:")
result_df.select(
    F.min("total_orders").alias("min_orders"),
    F.avg("total_orders").alias("avg_orders"),
    F.max("total_orders").alias("max_orders"),
    F.stddev("total_orders").alias("stddev_orders")
).show()

# ---------------------------------------------------------
# Step 7: Final action
# ---------------------------------------------------------
final = result_df.collect()
print(f"[INFO] Total groups returned: {len(final)}")


time.sleep(1300)
# input("\n[PAUSE]  (http://localhost:4040)...\n")


# spark.stop()
# print("[INFO] SparkSession stopped.")
