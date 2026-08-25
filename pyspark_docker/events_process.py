from pyspark.sql import SparkSession
import time

spark = (
    SparkSession.builder
    .appName("ExecutorTest")
    .config("spark.executor.cores", "1")
    .config("spark.executor.memory", "1g")
    .getOrCreate()
)

df = (
    spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/opt/spark-apps/data/events.csv")
)


print("Default parallelism:", spark.sparkContext.defaultParallelism)

df = df.repartition(8)

df.write.parquet("/opt/spark-apps/output/events")



print("JOB FINISHED — keeping application alive...")

time.sleep(1300)
