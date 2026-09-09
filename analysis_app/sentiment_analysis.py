#!/usr/bin/env python3
"""
情感分析脚本 - 基于规则的中文情感分析
不依赖外部NLP库，使用关键词词典进行正向/负向判断
"""

import mysql.connector
from mysql.connector import pooling
import re

# 数据库配置
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

# 正向情感词典（褒义词）
POSITIVE_WORDS = {
    # 赞美、满意
    '好', '棒', '优秀', '优质', '满意', '喜欢', '爱', '赞', '完美', '精彩',
    '出色', '卓越', '超群', '一流', '顶级', '高端', '豪华', '舒适', '静谧',
    '平顺', '流畅', '丝滑', '灵敏', '迅速', '强劲', '有劲', '省油', '经济',
    '实惠', '划算', '超值', '值得', '推荐', '信赖', '放心', '安心', '靠谱',
    # 外观赞美
    '漂亮', '好看', '帅气', '大气', '霸气', '时尚', '前卫', '动感', '优雅',
    '精致', '细腻', '考究', '用心', '独特', '个性', '辨识度', '气场', '高级感',
    # 空间舒适
    '宽敞', '宽裕', '充裕', '富裕', '大', '长', '高', '软', '支撑', '包裹',
    '腿部空间', '头部空间', '横向空间', '纵向空间', '一拳', '两拳', '三拳',
    # 配置丰富
    '丰富', '齐全', '完善', '高配', '顶配', '标配', '实用', '科技感', '智能',
    '便捷', '人性化', '贴心', '周到', '创新', '领先', '先进',
    # 驾驶体验
    '稳', '稳健', '扎实', '沉稳', '操控', '精准', '跟手', '响应', '轻快',
    '过弯', '侧倾', '抑制', '支撑性', '路感', '底盘', '调校', '舒适性',
    # 服务体验
    '热情', '专业', '耐心', '细致', '周到', '高效', '快速', '顺利', '愉快',
    '贴心', '负责', '诚信', '透明', '实在', '厚道',
    # 其他正向
    '惊喜', '超预期', '超过预期', '物超所值', '性价比', '高', '强', '快',
    '新', '新款', '升级', '改进', '优化', '提升', '增强', '改善', '解决'
}

# 负向情感词典（贬义词）
NEGATIVE_WORDS = {
    # 抱怨、不满
    '差', '烂', '垃圾', '糟糕', '失望', '后悔', '坑', '坑爹', '坑人', '不推荐',
    '不满意', '不喜欢', '讨厌', '恶心', '反感', '无语', '服了', '醉了',
    # 质量问题
    '故障', '毛病', '问题', '异响', '异味', '漏水', '漏油', '生锈', '脱漆',
    '剥落', '开裂', '变形', '断裂', '损坏', '失灵', '失效', '不工作', '不行',
    '不灵', '不准', '不灵敏', '迟钝', '卡顿', '死机', '重启', '黑屏', '花屏',
    # 空间不足
    '小', '窄', '紧', '局促', '拥挤', '压抑', '不够', '不足', '欠缺', '缺乏',
    '短', '低', '硬', '薄', '无支撑', '不包裹', '腰酸', '腿麻', '累',
    # 配置低
    '简配', '低配', '阉割', '缺失', '没有', '没', '无', '少', '寒酸', '简陋',
    '落后', '过时', '老旧', '陈旧', '廉价', '塑料感', '廉价感', '低级',
    # 驾驶体验差
    '飘', '散', '虚', '软', '跑偏', '跑偏', '方向盘', '打死', '沉重', '费劲',
    '颠簸', '硬朗', '生硬', '碎震', '不舒服', '晕车', '侧倾大', '支撑不足',
    '刹车', '软', '距离长', '不跟脚', '迟滞', '拖沓', '肉', '无力',
    # 油耗高
    '费油', '油耗高', '喝油', '烧油', '不省油', '不经济', '贵', '心疼',
    # 服务差
    '冷淡', '敷衍', '推诿', '拖延', '不专业', '不耐烦', '态度差', '爱理不理',
    '欺骗', '隐瞒', '套路', '坑', '宰客', '乱收费', '强制', '捆绑',
    # 噪音大
    '吵', '噪音大', '风噪', '胎噪', '发动机噪音', '共振', '嗡嗡', '嘎吱',
    # 其他负向
    '遗憾', '缺陷', '不足', '短板', '弱', '慢', '旧', '旧款', '降级', '减配',
    '取消', '去掉', '砍', '减少', '变差', '变丑', '变贵', '涨价', '不值', '亏'
}

# 否定词（会翻转情感）
NEGATION_WORDS = {
    '不', '没', '无', '非', '未', '否', '别', '莫', '勿', '休',
    '不是', '没有', '不是', '不曾', '未曾', '从未', '决不', '绝不',
    '毫不', '全不', '总不', '并不', '并未', '从不', '永不'
}

# 程度副词（增强情感）
DEGREE_WORDS = {
    '很': 1.5, '非常': 2.0, '特别': 2.0, '极其': 2.5, '十分': 2.0,
    '超级': 2.5, '超': 2.0, '太': 1.8, '真': 1.5, '确实': 1.5,
    '格外': 2.0, '分外': 2.0, '倍感': 2.0, '深感': 1.8
}

def segment_text(text):
    """简单的中文分词（按标点和常见词边界）"""
    # 这里使用简单的字符级和词级混合，实际可用jieba但这里不依赖外部库
    # 将文本按标点符号分句
    sentences = re.split(r'[。！？；，、,.!?;]', text)
    words = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        # 简单按字符处理，同时匹配多字词
        words.append(sent)
    return words

def calculate_sentiment(text):
    """
    计算文本情感倾向
    返回: (score, label, reason) 其中 label: 1=正向, 2=负向, 0=中性
    reason: 匹配到的关键词列表，用于解释判断依据
    """
    if not text or not text.strip():
        return 0, 0, "文本为空"
    
    text = text.strip()
    total_score = 0
    word_count = 0
    matched_positive = []
    matched_negative = []
    negated_positive = []
    negated_negative = []
    
    # 检查每个正向词
    for word in POSITIVE_WORDS:
        count = text.count(word)
        if count > 0:
            # 检查前面是否有否定词
            negated = False
            for neg in NEGATION_WORDS:
                # 简单检查：否定词在正向词前5个字符内
                pattern = neg + r'.{0,5}' + re.escape(word)
                if re.search(pattern, text):
                    negated = True
                    break
            
            if negated:
                total_score -= count * 1.0  # 否定正向 = 负向
                negated_positive.append(word)
            else:
                # 检查程度副词
                multiplier = 1.0
                for deg, mult in DEGREE_WORDS.items():
                    if deg + word in text or deg + ' ' + word in text:
                        multiplier = mult
                        break
                total_score += count * multiplier
                matched_positive.append(word)
            word_count += count
    
    # 检查每个负向词
    for word in NEGATIVE_WORDS:
        count = text.count(word)
        if count > 0:
            # 检查前面是否有否定词（否定负向 = 正向）
            negated = False
            for neg in NEGATION_WORDS:
                pattern = neg + r'.{0,5}' + re.escape(word)
                if re.search(pattern, text):
                    negated = True
                    break
            
            if negated:
                total_score += count * 1.0  # 否定负向 = 正向
                negated_negative.append(word)
            else:
                multiplier = 1.0
                for deg, mult in DEGREE_WORDS.items():
                    if deg + word in text or deg + ' ' + word in text:
                        multiplier = mult
                        break
                total_score -= count * multiplier
                matched_negative.append(word)
            word_count += count
    
    # 归一化得分
    if word_count == 0:
        return 0, 0, "未匹配到情感词汇"
    
    avg_score = total_score / max(word_count, 1)
    
    # 构建推理说明
    reason_parts = []
    if matched_positive:
        reason_parts.append(f"正向词: {', '.join(set(matched_positive))}")
    if matched_negative:
        reason_parts.append(f"负向词: {', '.join(set(matched_negative))}")
    if negated_positive:
        reason_parts.append(f"否定正向词: {', '.join(set(negated_positive))}")
    if negated_negative:
        reason_parts.append(f"否定负向词: {', '.join(set(negated_negative))}")
    reason = "; ".join(reason_parts) if reason_parts else "未匹配到情感词汇"
    
    # 判断标签：1=正向, 2=负向, 0=中性
    if avg_score > 0.1:
        return avg_score, 1, reason  # 正向
    elif avg_score < -0.1:
        return avg_score, 2, reason  # 负向
    else:
        return avg_score, 0, reason  # 中性

def add_sentiment_column():
    """为 Label_data 表添加 sentiment 和 sentiment_reason 列"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查列是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'aivoc' AND TABLE_NAME = 'Label_data' AND COLUMN_NAME = 'sentiment'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE Label_data 
                ADD COLUMN sentiment TINYINT DEFAULT 0 COMMENT '情感倾向: 1=正向, 2=负向, 0=中性'
            """)
            conn.commit()
            print("✅ 已添加 sentiment 列")
        else:
            print("ℹ️ sentiment 列已存在")
        
        # 检查 sentiment_reason 列
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'aivoc' AND TABLE_NAME = 'Label_data' AND COLUMN_NAME = 'sentiment_reason'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE Label_data 
                ADD COLUMN sentiment_reason TEXT COMMENT '情感分析依据: 记录判断为正向/负向/中性的关键词依据'
            """)
            conn.commit()
            print("✅ 已添加 sentiment_reason 列")
        else:
            print("ℹ️ sentiment_reason 列已存在")
    except Exception as e:
        print(f"❌ 添加列失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def analyze_and_update():
    """分析 txt_data 文本并更新 Label_data 表"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取所有 txt_data 记录
        cursor.execute("SELECT data_code, text_content FROM txt_data")
        texts = cursor.fetchall()
        
        print(f"📊 共 {len(texts)} 条原始文本待分析")
        
        results = []
        for row in texts:
            data_code = row['data_code']
            text_content = row['text_content'] or ''
            
            score, label, reason = calculate_sentiment(text_content)
            
            results.append({
                'data_code': data_code,
                'text_preview': text_content[:50] + '...' if len(text_content) > 50 else text_content,
                'score': round(score, 3),
                'sentiment': label,
                'sentiment_label': {1: '正向', 2: '负向', 0: '中性'}[label],
                'reason': reason
            })
            
            print(f"  {data_code}: 得分={score:.3f} -> {results[-1]['sentiment_label']}")
            print(f"    依据: {reason}")
        
        # 更新 Label_data 表：为每个 data_code 设置相同的情感标签和依据
        # 因为 Label_data 中同一 data_code 可能有多行，我们为每行都设置
        for r in results:
            cursor.execute("""
                UPDATE Label_data 
                SET sentiment = %s, sentiment_reason = %s
                WHERE data_code = %s
            """, (r['sentiment'], r['reason'], r['data_code']))
        
        conn.commit()
        print(f"\n✅ 已更新 {cursor.rowcount} 条 Label_data 记录")
        
        return results
        
    except Exception as e:
        print(f"❌ 分析更新失败: {e}")
        conn.rollback()
        return []
    finally:
        cursor.close()
        conn.close()

def generate_report(results):
    """生成中文分析报告"""
    if not results:
        return "❌ 无分析结果"
    
    total = len(results)
    positive = sum(1 for r in results if r['sentiment'] == 1)
    negative = sum(1 for r in results if r['sentiment'] == 2)
    neutral = sum(1 for r in results if r['sentiment'] == 0)
    
    # 按数据编号统计
    by_code = {}
    for r in results:
        code = r['data_code']
        if code not in by_code:
            by_code[code] = {'pos': 0, 'neg': 0, 'neu': 0, 'total': 0}
        by_code[code]['total'] += 1
        if r['sentiment'] == 1:
            by_code[code]['pos'] += 1
        elif r['sentiment'] == 2:
            by_code[code]['neg'] += 1
        else:
            by_code[code]['neu'] += 1
    
    report = []
    report.append("=" * 60)
    report.append("📋 语义情感分析报告")
    report.append("=" * 60)
    report.append(f"\n📊 总体统计:")
    report.append(f"   总记录数: {total}")
    report.append(f"   正向(褒义): {positive} ({positive/total*100:.1f}%)")
    report.append(f"   负向(贬义): {negative} ({negative/total*100:.1f}%)")
    report.append(f"   中性: {neutral} ({neutral/total*100:.1f}%)")
    
    report.append(f"\n📝 按数据编号统计:")
    for code, stats in by_code.items():
        report.append(f"   {code}: 总计{stats['total']}条 | 正向{stats['pos']} | 负向{stats['neg']} | 中性{stats['neu']}")
    
    report.append(f"\n📄 详细结果:")
    for r in results:
        report.append(f"   [{r['sentiment_label']}] {r['data_code']} (得分:{r['score']:.3f})")
        report.append(f"      文本摘要: {r['text_preview']}")
        report.append(f"      分析依据: {r['reason']}")
        report.append("")
    
    report.append("\n" + "=" * 60)
    report.append("分析完成 | 基于规则的中文情感词典分析")
    report.append("标签说明: 1=正向(褒义), 2=负向(贬义), 0=中性")
    report.append("=" * 60)
    
    return "\n".join(report)

def verify_update():
    """验证更新结果"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT data_code, sentiment, COUNT(*) as cnt FROM Label_data GROUP BY data_code, sentiment ORDER BY data_code, sentiment")
        rows = cursor.fetchall()
        
        print("\n🔍 验证更新结果:")
        for r in rows:
            label = {1: '正向', 2: '负向', 0: '中性'}.get(r['sentiment'], '未知')
            print(f"   {r['data_code']}: {label} = {r['cnt']} 条")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("🚀 开始情感分析流程...")
    print("-" * 40)
    
    # 1. 添加列
    add_sentiment_column()
    
    # 2. 分析并更新
    results = analyze_and_update()
    
    # 3. 验证
    verify_update()
    
    # 4. 生成报告
    report = generate_report(results)
    print("\n" + report)
    
    # 保存报告到文件
    with open('/home/shaun/voc-ai/analysis_app/sentiment_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("\n📁 报告已保存至: /home/shaun/voc-ai/analysis_app/sentiment_report.txt")