USE insta_engagement;
CREATE TABLE IF NOT EXISTS instagram_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    follower_count BIGINT,
    following_count INT,
    media_count INT,
    is_verified BOOLEAN,
    category VARCHAR(255),
    biography TEXT,
    profile_pic_url_hd TEXT,
    external_url TEXT,
    is_private BOOLEAN,
    account_type ENUM('Personal', 'Business'),
    status ENUM('success', 'failed')
);
CREATE TABLE IF NOT EXISTS bio_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    title TEXT,
    url TEXT,
    FOREIGN KEY (username)
        REFERENCES instagram_profiles (username)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS instagram_posts (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255),
    code VARCHAR(255),
    thumbnail_url VARCHAR(2048),
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    caption TEXT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username)
        REFERENCES instagram_profiles (username)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS instagram_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id VARCHAR(255),
    username VARCHAR(255),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id)
        REFERENCES instagram_posts (id)
        ON DELETE CASCADE
);
desc instagram_comments;
desc instagram_profiles;
SELECT 
    *
FROM
    instagram_profiles;
    
SELECT 
    *
FROM
    instagram_posts;

desc bio_links;
SELECT 
    *
FROM
    bio_links;
SELECT * FROM instagram_comments;
    
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE bio_links;
TRUNCATE TABLE instagram_profiles;
truncate table instagram_posts;
SET FOREIGN_KEY_CHECKS = 1;


SELECT 
    ip.username,
    ip.follower_count,
    COALESCE(SUM(ipost.like_count), 0) AS total_likes,
    COALESCE(SUM(ipost.comment_count), 0) AS total_comments,
    COALESCE(
        (SUM(ipost.comment_count)) / NULLIF(ip.follower_count, 0) * 100,
        0
    ) AS engagement_rate
FROM instagram_profiles ip
LEFT JOIN instagram_posts ipost ON ip.username = ipost.username
GROUP BY ip.username, ip.follower_count
ORDER BY engagement_rate DESC;
