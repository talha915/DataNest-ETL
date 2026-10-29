from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import random

spark = (
    SparkSession.builder
    .appName("SkewDemo")
    .config("spark.driver.host", "spark-client")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.sql.adaptive.enabled", "false")
    .getOrCreate()
)


df = spark.range(0, 10_000_000) \
    .withColumn("key", 
        when(rand() < 0.9, lit("HOT_KEY"))
        .otherwise(concat(lit("key_"), (rand() * 100).cast("int")))
    ) \
    .select("key", col("id").alias("value"))

df = df.repartition(8, "key")

df.count() 

print("Running groupBy...")
result = df.groupBy("key").count()
result.show()


input("\n⏸️  Press Enter to stop...")

spark.stop()
