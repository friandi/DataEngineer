from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType



# KAFKA_BROKER = "localhost:29092,localhost:30092,localhost:49092"
KAFKA_BROKER = "kafka-broker-1:19092,kafka-broker-2:19092,kafka-broker-3:19092"
SOURCE_TOPIC = 'financial_transactions'
AGGREGATES_TOPIC = 'transactions_aggregates'
ANOMALIES_TOPIC = 'transactions_anomalies'
CHECKPOINT_DIR = '/mnt/spark-checkpoints'
STATES_DIR = '/mnt/spark-state'



spark = (SparkSession.builder
         .appName('FinancialTransactionsProcessor')
         .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0')
         .config('spark.sql.streaming.checkpointLocation', CHECKPOINT_DIR)
         .config('spark.sql.streaming.stateStore.stateStoreDir', STATES_DIR)
         .config('spark.sql.shuffle.partitions', 3)
         
).getOrCreate()

spark.sparkContext.setLogLevel("WARN")

transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("userId", StringType(), True),
    StructField("merchantId", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transactionTime", LongType(), True),
    StructField("transactionType", StringType(), True),
    StructField("location", StringType(), True),
    StructField("paymentMethod", StringType(), True),
    StructField("isInternational", StringType(), True),
    StructField("currency", StringType(), True)
])


kafka_stream = (spark.readStream
                .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", SOURCE_TOPIC)
    .option("startingOffsets", "earliest")
    ).load()

transaction_df = kafka_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), transaction_schema).alias("data")) \
    .select("data.*")   


transaction_df = transaction_df.withColumn("transactionTimestamp", (col("transactionTime") / 1000).cast("timestamp"))

aggregated_df = transaction_df.groupBy("merchantId")\
    .agg(
        sum("amount").alias("total_amount"),
        count("*").alias("transaction_count")
    )

aggregation_query = (
    aggregated_df.withColumn("key", col("merchantId").cast("string"))
    .withColumn("value", to_json(struct(
        col("merchantId"),
        col("total_amount"),
        col("transaction_count")
    )))
    .selectExpr("key", "value")
    .writeStream
    .format("kafka")
    .outputMode("update")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("topic", AGGREGATES_TOPIC)
    .option("checkpointLocation", f'{CHECKPOINT_DIR}/aggregates')
    .start().awaitTermination()
)
