-- ForumKit D1 Database Schema

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    email_hash TEXT UNIQUE NOT NULL,
    username TEXT,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    role TEXT DEFAULT 'user' NOT NULL,
    school_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

-- Schools table
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME
);

-- Posts table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT TRUE NOT NULL,
    author_id INTEGER,
    school_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    is_sensitive BOOLEAN DEFAULT FALSE NOT NULL,
    sensitive_reason TEXT,
    reviewed_by INTEGER,
    reviewed_at DATETIME,
    review_comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    deleted_at DATETIME,
    view_count INTEGER DEFAULT 0 NOT NULL,
    like_count INTEGER DEFAULT 0 NOT NULL,
    comment_count INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id),
    FOREIGN KEY (reviewed_by) REFERENCES users (id)
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT TRUE NOT NULL,
    author_id INTEGER,
    post_id INTEGER NOT NULL,
    parent_id INTEGER,
    school_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    reviewed_by INTEGER,
    reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    deleted_at DATETIME,
    like_count INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id),
    FOREIGN KEY (parent_id) REFERENCES comments (id),
    FOREIGN KEY (school_id) REFERENCES schools (id),
    FOREIGN KEY (reviewed_by) REFERENCES users (id)
);

-- Review logs table
CREATE TABLE review_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts (id),
    FOREIGN KEY (reviewer_id) REFERENCES users (id)
);

-- Global discussions table
CREATE TABLE global_discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    reviewed_by INTEGER,
    reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    deleted_at DATETIME,
    view_count INTEGER DEFAULT 0 NOT NULL,
    like_count INTEGER DEFAULT 0 NOT NULL,
    comment_count INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users (id),
    FOREIGN KEY (reviewed_by) REFERENCES users (id)
);

-- Global review logs table
CREATE TABLE global_review_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- School feature toggles table
CREATE TABLE school_feature_toggles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    enabled_by INTEGER,
    enabled_at DATETIME,
    disabled_at DATETIME,
    config_data TEXT, -- JSON string for additional config
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    UNIQUE(school_id, feature_name),
    FOREIGN KEY (school_id) REFERENCES schools (id),
    FOREIGN KEY (enabled_by) REFERENCES users (id)
);

-- Admin logs table
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT, -- user, post, comment, etc.
    target_id INTEGER,
    details TEXT, -- JSON string for additional details
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES users (id)
);

-- Discord settings table
CREATE TABLE discord_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    webhook_url TEXT NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

-- Instagram accounts table
CREATE TABLE ig_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME
);

-- Instagram templates table
CREATE TABLE ig_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    template_path TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_school_id ON users(school_id);
CREATE INDEX idx_posts_school_id ON posts(school_id);
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_review_logs_post_id ON review_logs(post_id);
CREATE INDEX idx_global_discussions_author_id ON global_discussions(author_id);
CREATE INDEX idx_school_feature_toggles_school_id ON school_feature_toggles(school_id); 