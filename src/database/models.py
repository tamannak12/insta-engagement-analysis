"""
Database models for Instagram engagement analysis project.
This file defines the database schema and table structure.
"""

# SQL statements to create necessary tables
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS instagram_profiles (
        username VARCHAR(255) PRIMARY KEY,
        full_name VARCHAR(255),
        follower_count INT,
        following_count INT,
        media_count INT,
        is_verified BOOLEAN,
        category VARCHAR(255),
        biography TEXT,
        profile_pic_url_hd VARCHAR(512),
        external_url VARCHAR(512),
        is_private BOOLEAN,
        account_type VARCHAR(50),
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bio_links (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        title VARCHAR(255),
        url VARCHAR(512),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES instagram_profiles(username) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_bio_links_username ON bio_links(username)
    """,
    """
    CREATE TABLE IF NOT EXISTS instagram_posts (
        id VARCHAR(255) PRIMARY KEY,
        username VARCHAR(255),
        code VARCHAR(255),
        thumbnail_url VARCHAR(512),
        like_count INT DEFAULT 0,
        comment_count INT DEFAULT 0,
        caption TEXT,
        timestamp TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES instagram_profiles(username) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_instagram_posts_username ON instagram_posts(username)
    """

]

def initialize_database(connection):
    """Initialize database by creating necessary tables.
    
    Args:
        connection: MySQL database connection
    """
    cursor = connection.cursor()
    
    try:
        for sql in CREATE_TABLES_SQL:
            cursor.execute(sql)
        connection.commit()
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        connection.rollback()
    finally:
        cursor.close()
        
CREATE_TABLES_SQL.append("""
    CREATE TABLE IF NOT EXISTS instagram_comments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        post_id VARCHAR(255),
        username VARCHAR(255),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES instagram_posts(id) ON DELETE CASCADE
    )
""")
CREATE_TABLES_SQL.append("""
    CREATE INDEX IF NOT EXISTS idx_instagram_comments_post_id ON instagram_comments(post_id)
""")