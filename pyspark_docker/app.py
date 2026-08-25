from pyspark.sql import SparkSession
import time

spark = (
    SparkSession.builder
    .appName("ExecutorTest")
    .config("spark.executor.cores", "1")
    .config("spark.executor.memory", "1g")
    .getOrCreate()
)

sc = spark.sparkContext

print("Master:", sc.master)
print("Default parallelism:", sc.defaultParallelism)

df = spark.range(0, 10_000_000, numPartitions=8)

print("Partitions:", df.rdd.getNumPartitions())
print("Count:", df.count())

print("JOB FINISHED — keeping application alive...")

time.sleep(300)

# spark.stop()