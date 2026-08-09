CREATE TABLE IF NOT EXISTS product_sentiment_windows (
    timestamp DateTime,
    product_keyword String,
    positive_count UInt32,
    neutral_count UInt32,
    negative_count UInt32,
    avg_confidence Float32
) ENGINE = MergeTree()
ORDER BY (timestamp, product_keyword);
