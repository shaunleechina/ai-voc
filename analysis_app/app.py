from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import pooling
import json

app = Flask(__name__)

# 数据库连接池配置
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'pool_name': 'mypool',
    'pool_size': 5
}

# 创建连接池
connection_pool = pooling.MySQLConnectionPool(**db_config)

def get_db_connection():
    return connection_pool.get_connection()

@app.route('/')
def index():
    """主页 - 显示分类统计"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取所有match_type及其统计
    cursor.execute("""
        SELECT 
            match_type,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT match_detail) as match_details,
            GROUP_CONCAT(DISTINCT data_code) as data_codes
        FROM Label_data 
        WHERE match_type IS NOT NULL AND match_type != ''
        GROUP BY match_type
        ORDER BY count DESC
    """)
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 处理数据格式供模板使用
    for cat in categories:
        cat['match_details'] = cat['match_details'].split(',') if cat['match_details'] else []
        cat['data_codes'] = cat['data_codes'].split(',') if cat['data_codes'] else []
    
    return render_template('index.html', categories=categories)


@app.route('/api/categories')
def api_categories():
    """API: 获取所有分类数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            match_type,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT match_detail) as match_details,
            GROUP_CONCAT(DISTINCT data_code) as data_codes
        FROM Label_data 
        WHERE match_type IS NOT NULL AND match_type != ''
        GROUP BY match_type
        ORDER BY count DESC
    """)
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for cat in categories:
        cat['match_details'] = cat['match_details'].split(',') if cat['match_details'] else []
        cat['data_codes'] = cat['data_codes'].split(',') if cat['data_codes'] else []
    
    return jsonify(categories)

@app.route('/api/category/<match_type>')
def get_category_detail(match_type):
    """获取特定分类的详细数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            id,
            code_table_name,
            full_code,
            data_code,
            match_type,
            match_detail,
            sentiment,
            sentiment_reason,
            original_sentence,
            created_at
        FROM Label_data 
        WHERE match_type = %s
        ORDER BY id
    """, (match_type,))
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(records)

@app.route('/api/text/<data_code>')
def get_text_detail(data_code):
    """获取文本详细内容"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            id,
            data_code,
            data_source,
            text_content,
            text_length,
            created_at
        FROM txt_data 
        WHERE data_code = %s
    """, (data_code,))
    record = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if record:
        return jsonify(record)
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/search')
def search():
    """搜索功能"""
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            ld.id,
            ld.code_table_name,
            ld.full_code,
            ld.data_code,
            ld.match_type,
            ld.match_detail,
            td.text_content
        FROM Label_data ld
        LEFT JOIN txt_data td ON ld.data_code = td.data_code
        WHERE ld.match_type LIKE %s 
           OR ld.match_detail LIKE %s
           OR ld.data_code LIKE %s
           OR td.text_content LIKE %s
        LIMIT 100
    """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)


@app.route('/data')
def data_index():
    """数据分类页面 - 按 data_code 分组"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取所有 data_code 及其标签数量
    cursor.execute("""
        SELECT 
            td.data_code,
            td.data_source,
            td.text_length,
            COUNT(ld.id) as label_count,
            GROUP_CONCAT(DISTINCT ld.match_type) as match_types,
            GROUP_CONCAT(DISTINCT ld.match_detail) as match_details
        FROM txt_data td
        LEFT JOIN Label_data ld ON td.data_code = ld.data_code
        GROUP BY td.data_code, td.data_source, td.text_length
        ORDER BY td.data_code
    """)
    data_records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 处理数据格式
    for rec in data_records:
        rec['match_types'] = rec['match_types'].split(',') if rec['match_types'] else []
        rec['match_details'] = rec['match_details'].split(',') if rec['match_details'] else []
    
    return render_template('data.html', data_records=data_records)


@app.route('/api/data_codes')
def api_data_codes():
    """API: 获取所有数据编号及统计"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取基础数据
    cursor.execute("""
        SELECT 
            td.data_code,
            td.data_source,
            td.text_length,
            COUNT(ld.id) as label_count,
            GROUP_CONCAT(DISTINCT ld.match_type) as match_types,
            GROUP_CONCAT(DISTINCT ld.match_detail) as match_details,
            GROUP_CONCAT(DISTINCT ld.data_code) as data_codes
        FROM txt_data td
        LEFT JOIN Label_data ld ON td.data_code = ld.data_code
        GROUP BY td.data_code, td.data_source, td.text_length
        ORDER BY td.data_code
    """)
    data_records = cursor.fetchall()
    
    # 获取每个 data_code 的情感统计
    for rec in data_records:
        rec['match_types'] = rec['match_types'].split(',') if rec['match_types'] else []
        rec['match_details'] = rec['match_details'].split(',') if rec['match_details'] else []
        rec['data_codes'] = rec['data_codes'].split(',') if rec['data_codes'] else []
        
        # 查询情感统计
        cursor.execute("""
            SELECT 
                sentiment,
                COUNT(*) as count
            FROM Label_data
            WHERE data_code = %s
            GROUP BY sentiment
        """, (rec['data_code'],))
        sentiment_results = cursor.fetchall()
        
        sentiments = {}
        for sr in sentiment_results:
            sentiments[str(sr['sentiment'])] = {
                'count': sr['count'],
                'match_types': [],
                'data_codes': []
            }
        # 确保三种情感都存在
        for s in ['1', '2', '0']:
            if s not in sentiments:
                sentiments[s] = {'count': 0, 'match_types': [], 'data_codes': []}
        rec['sentiments'] = sentiments
    
    cursor.close()
    conn.close()
    
    return jsonify(data_records)


@app.route('/api/labels/<data_code>')
def get_labels_by_data_code(data_code):
    """获取某 data_code 下的所有标签"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            id,
            code_table_name,
            full_code,
            data_code,
            match_type,
            match_detail,
            sentiment,
            sentiment_reason,
            original_sentence,
            created_at
        FROM Label_data 
        WHERE data_code = %s
        ORDER BY match_type, id
    """, (data_code,))
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(records)


@app.route('/sentiment')
def sentiment_index():
    """情感倾向分类页面"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 按 sentiment 分组统计
    cursor.execute("""
        SELECT 
            sentiment,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT match_type) as match_types,
            GROUP_CONCAT(DISTINCT data_code) as data_codes
        FROM Label_data 
        WHERE sentiment IS NOT NULL
        GROUP BY sentiment
        ORDER BY sentiment
    """)
    sentiment_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 处理数据
    for s in sentiment_stats:
        s['match_types'] = s['match_types'].split(',') if s['match_types'] else []
        s['data_codes'] = s['data_codes'].split(',') if s['data_codes'] else []
        s['sentiment_label'] = {1: '正向褒义', 2: '负向贬义', 0: '中性'}.get(s['sentiment'], '未知')
        s['sentiment_color'] = {1: '#166534', 2: '#b91c1c', 0: '#6b7280'}.get(s['sentiment'], '#6b7280')
        s['sentiment_bg'] = {1: '#f0fdf4', 2: '#fef2f2', 0: '#f3f4f6'}.get(s['sentiment'], '#f3f4f6')
    
    return render_template('sentiment.html', sentiment_stats=sentiment_stats)


@app.route('/api/sentiment/<int:sentiment>')
def get_sentiment_detail(sentiment):
    """获取特定情感倾向的详细数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            id,
            code_table_name,
            full_code,
            data_code,
            match_type,
            match_detail,
            sentiment,
            sentiment_reason,
            original_sentence,
            created_at
        FROM Label_data 
        WHERE sentiment = %s
        ORDER BY data_code, match_type, id
    """, (sentiment,))
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(records)


@app.route('/api/sentiment_stats')
def api_sentiment_stats():
    """API: 获取情感倾向统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            sentiment,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT match_type) as match_types,
            GROUP_CONCAT(DISTINCT data_code) as data_codes
        FROM Label_data 
        WHERE sentiment IS NOT NULL
        GROUP BY sentiment
        ORDER BY sentiment
    """)
    sentiment_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for s in sentiment_stats:
        s['match_types'] = s['match_types'].split(',') if s['match_types'] else []
        s['data_codes'] = s['data_codes'].split(',') if s['data_codes'] else []
        s['sentiment_label'] = {1: '正向褒义', 2: '负向贬义', 0: '中性'}.get(s['sentiment'], '未知')
        s['sentiment_color'] = {1: '#166534', 2: '#b91c1c', 0: '#6b7280'}.get(s['sentiment'], '#6b7280')
        s['sentiment_bg'] = {1: '#f0fdf4', 2: '#fef2f2', 0: '#f3f4f6'}.get(s['sentiment'], '#f3f4f6')
    
    return jsonify(sentiment_stats)


@app.route('/api/sentiment_detail')
def api_sentiment_detail():
    """API: 根据代码表、一级代码和情感倾向获取明细记录"""
    code_table = request.args.get('code_table')
    first_code = request.args.get('first_code')
    sentiment = request.args.get('sentiment', type=int)
    match_type = request.args.get('match_type')
    data_code = request.args.get('data_code')

    if not code_table or sentiment is None:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            id, code_table_name, full_code, data_code, match_type,
            match_detail, sentiment, sentiment_reason, original_sentence, created_at
        FROM Label_data 
        WHERE code_table_name = %s AND sentiment = %s
    """
    params = [code_table, sentiment]

    if first_code:
        sql += " AND LEFT(full_code, 2) = %s"
        params.append(first_code)
    if match_type:
        sql += " AND match_type = %s"
        params.append(match_type)
    if data_code:
        sql += " AND data_code = %s"
        params.append(data_code)

    sql += " ORDER BY data_code, match_type, id"

    cursor.execute(sql, tuple(params))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records)


@app.route('/api/sentiment_by_firstcode')
def api_sentiment_by_firstcode():
    """API: 按一级代码分组的情感统计，可选按代码表过滤"""
    code_table = request.args.get('code_table')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 从对应的代码表中查询一级代码的中文名称
    first_code_names = {}
    if code_table:
        cursor.execute(
            f"SELECT full_code, full_name FROM {code_table} WHERE level = 1"
        )
        for row in cursor.fetchall():
            first_code_names[row['full_code']] = row['full_name']

    sql = """
        SELECT 
            LEFT(full_code, 2) as first_code,
            code_table_name,
            sentiment,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT match_type) as match_types,
            GROUP_CONCAT(DISTINCT data_code) as data_codes
        FROM Label_data 
        WHERE sentiment IS NOT NULL
    """
    params = []
    if code_table:
        sql += " AND code_table_name = %s"
        params.append(code_table)
    sql += " GROUP BY first_code, code_table_name, sentiment ORDER BY first_code, code_table_name, sentiment"

    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    result = {}
    for r in rows:
        fc = r['first_code']
        ct = r['code_table_name']
        sent = r['sentiment']
        if fc not in result:
            result[fc] = {}
        if ct not in result[fc]:
            result[fc][ct] = {1: None, 2: None, 0: None}
        result[fc][ct][sent] = {
            'count': r['count'],
            'match_types': r['match_types'].split(',') if r['match_types'] else [],
            'data_codes': r['data_codes'].split(',') if r['data_codes'] else []
        }

    output = []
    for fc in sorted(result.keys()):
        tables = []
        for ct, sentiments in result[fc].items():
            tables.append({
                'code_table_name': ct,
                'sentiments': {
                    1: sentiments[1] or {'count':0,'match_types':[],'data_codes':[]},
                    2: sentiments[2] or {'count':0,'match_types':[],'data_codes':[]},
                    0: sentiments[0] or {'count':0,'match_types':[],'data_codes':[]},
                }
            })
        output.append({
            'first_code': fc,
            'first_code_name': first_code_names.get(fc, '未知'),
            'tables': tables
        })

    return jsonify(output)


@app.route('/element_code')
def element_code_index():
    """元素代码表页面"""
    return render_template('code_table.html', code_table='element_code', code_table_cn='元素代码表')


@app.route('/indicator_code')
def indicator_code_index():
    """指标代码表页面"""
    return render_template('code_table.html', code_table='indicator_code', code_table_cn='指标代码表')


@app.route('/evaluation_code')
def evaluation_code_index():
    """评价代码表页面"""
    return render_template('code_table.html', code_table='evaluation_code', code_table_cn='评价代码表')


if __name__ == '__main__':
    # 允许局域网访问
    app.run(host='0.0.0.0', port=8080, debug=False)
