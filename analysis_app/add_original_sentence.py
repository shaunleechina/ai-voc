#!/usr/bin/env python3
"""
为 Label_data 表新增 original_sentence 列，并填入每条记录对应的关键判断句子。
"""

import mysql.connector
from mysql.connector import pooling
import re

db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'pool_name': 'mypool',
    'pool_size': 5
}
connection_pool = pooling.MySQLConnectionPool(**db_config)

def get_db_connection():
    return connection_pool.get_connection()

def add_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA='aivoc' AND TABLE_NAME='Label_data' AND COLUMN_NAME='original_sentence'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE Label_data
                ADD COLUMN original_sentence TEXT COMMENT '作为情感判断依据的关键原文句子'
            """)
            conn.commit()
            print("✅ 已添加 original_sentence 列")
        else:
            print("ℹ️ original_sentence 列已存在")
    finally:
        cursor.close()
        conn.close()

def split_sentences(text):
    """按中文标点分句，保留标点"""
    # 使用正则按 。！？ 分割，保留分隔符
    parts = re.split(r'([。！？])', text)
    sentences = []
    for i in range(0, len(parts)-1, 2):
        sent = parts[i].strip()
        punct = parts[i+1] if i+1 < len(parts) else ''
        if sent:
            sentences.append(sent + punct)
    # 处理可能没有标点的尾部
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1].strip())
    return sentences

def find_key_sentence(text_content, keywords):
    """在文本中找到包含任一关键词的第一句"""
    sentences = split_sentences(text_content)
    kw_list = [k.strip() for k in keywords.replace('匹配关键词:', '').split(',') if k.strip()]
    for sent in sentences:
        for kw in kw_list:
            if kw in sent:
                return sent
    # 兜底：返回前 200 字符
    return text_content[:200]

def process():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 获取文本
    cursor.execute("SELECT data_code, text_content FROM txt_data")
    texts = {row['data_code']: row['text_content'] for row in cursor.fetchall()}
    # 获取标签
    cursor.execute("SELECT id, data_code, match_detail FROM Label_data ORDER BY id")
    labels = cursor.fetchall()
    print(f"共 {len(labels)} 条记录待处理")
    for i, lab in enumerate(labels, 1):
        data_code = lab['data_code']
        match_detail = lab['match_detail'] or ''
        text_content = texts.get(data_code, '')
        key_sent = find_key_sentence(text_content, match_detail)
        # 更新
        cursor.execute("""
            UPDATE Label_data SET original_sentence = %s WHERE id = %s
        """, (key_sent, lab['id']))
        if i % 20 == 0:
            conn.commit()
            print(f"  已处理 {i}/{len(labels)}")
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 完成")

if __name__ == '__main__':
    add_column()
    process()