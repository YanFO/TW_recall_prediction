-- 初始化資料庫結構
-- 台灣罷免預測分析系統

-- 建立文章資料表
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    author VARCHAR(100),
    source VARCHAR(50) NOT NULL,
    board VARCHAR(100),
    forum VARCHAR(100),
    link TEXT,
    created_at TIMESTAMP,
    crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0
);

-- 建立情緒分析結果表
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(5,3),
    sentiment_confidence DECIMAL(5,3),
    recall_stance VARCHAR(30),
    stance_confidence DECIMAL(5,3),
    positive_words INTEGER DEFAULT 0,
    negative_words INTEGER DEFAULT 0,
    support_signals INTEGER DEFAULT 0,
    oppose_signals INTEGER DEFAULT 0,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立人口統計分類表
CREATE TABLE IF NOT EXISTS demographics (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    age_group VARCHAR(20),
    region VARCHAR(20),
    occupation VARCHAR(30),
    classification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立議題分析表
CREATE TABLE IF NOT EXISTS issue_analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    political_issues TEXT,
    recall_reasons TEXT,
    issue_count INTEGER DEFAULT 0,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立預測結果表
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL,
    support_rate DECIMAL(5,3),
    prediction_result VARCHAR(10),
    confidence DECIMAL(5,3),
    sample_size INTEGER,
    model_accuracy DECIMAL(5,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立系統日誌表
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(10),
    message TEXT,
    component VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引以提升查詢性能
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_crawl_time ON articles(crawl_time);
CREATE INDEX IF NOT EXISTS idx_sentiment_article_id ON sentiment_analysis(article_id);
CREATE INDEX IF NOT EXISTS idx_demographics_article_id ON demographics(article_id);
CREATE INDEX IF NOT EXISTS idx_issue_article_id ON issue_analysis(article_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system_logs(created_at);

-- 建立視圖以簡化查詢
CREATE OR REPLACE VIEW article_analysis_summary AS
SELECT 
    a.id,
    a.title,
    a.source,
    a.board,
    a.created_at,
    s.sentiment,
    s.sentiment_score,
    s.recall_stance,
    d.age_group,
    d.region,
    d.occupation,
    i.political_issues,
    i.recall_reasons
FROM articles a
LEFT JOIN sentiment_analysis s ON a.id = s.article_id
LEFT JOIN demographics d ON a.id = d.article_id
LEFT JOIN issue_analysis i ON a.id = i.article_id;

-- 建立每日統計視圖
CREATE OR REPLACE VIEW daily_statistics AS
SELECT 
    DATE(a.crawl_time) as analysis_date,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN s.sentiment = 'positive' THEN 1 END) as positive_count,
    COUNT(CASE WHEN s.sentiment = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN s.sentiment = 'neutral' THEN 1 END) as neutral_count,
    COUNT(CASE WHEN s.recall_stance = 'support_recall' THEN 1 END) as support_count,
    COUNT(CASE WHEN s.recall_stance = 'oppose_recall' THEN 1 END) as oppose_count,
    AVG(s.sentiment_score) as avg_sentiment_score,
    AVG(s.stance_confidence) as avg_stance_confidence
FROM articles a
LEFT JOIN sentiment_analysis s ON a.id = s.article_id
GROUP BY DATE(a.crawl_time)
ORDER BY analysis_date DESC;

-- 插入初始配置資料
INSERT INTO system_logs (log_level, message, component) 
VALUES ('INFO', '資料庫初始化完成', 'database_init')
ON CONFLICT DO NOTHING;
