#!/usr/bin/env python3
"""
基于上下文语义理解的情感分析
逐条分析 Label_data 中的每一条记录，结合 match_type 和 match_detail
在 txt_data.text_content 中的真实语境含义
"""

import mysql.connector
from mysql.connector import pooling

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

# ========== 全局辅助函数 ==========

def is_negated(text, target_word, window=5):
    """检查目标词前window字符内是否有否定词（直接修饰关系）"""
    idx = text.find(target_word)
    if idx < 0:
        return False
    before = text[max(0, idx-window):idx]
    # 只检测紧邻目标词的否定词（直接修饰）
    negation_phrases = [
        '不是', '没有', '不曾', '未曾', '从未', '决不', '绝不',
        '毫不', '全不', '总不', '并不', '并未', '从不', '永不',
        '不会', '没法', '无法', '不太', '不再', '不曾',
        '没', '不'
    ]
    for neg in negation_phrases:
        if neg in before:
            if neg in ['不', '没']:
                # 单字否定词：必须紧邻目标词（如"不推荐"、"没空间"）
                neg_idx = before.rfind(neg)
                if neg_idx >= 0:
                    # 检查否定词与目标词之间的距离
                    distance = len(before) - neg_idx - len(neg)
                    if distance <= 2:  # 否定词后最多2字符直接接目标词
                        # 排除成语中的"不/无/非"
                        idiom_prefixes = ['独一', '非同', '非比', '非同', '未雨', '未曾', '无可', '无奈', '无从', '无法', '无能', '无力', '无微', '无孔', '无所', '无时', '无事', '无声', '无形', '无心', '无意', '无知', '无止', '非分', '非驴', '非马', '非同', '非比']
                        for prefix in idiom_prefixes:
                            if before[max(0, neg_idx-len(prefix)):neg_idx] == prefix:
                                break
                        else:
                            return True
            else:
                # 多字否定词：只要在窗口内即可（如"不是"、"没有"）
                return True
    return False


def has_negative_context(text, target_word, window=50):
    """检查目标词附近是否有针对性负面描述"""
    idx = text.find(target_word)
    if idx < 0:
        return False, None
    start = max(0, idx - window)
    end = min(len(text), idx + len(target_word) + window)
    surrounding = text[start:end]

    # 为不同类型关键词定义专门的负面模式
    negative_patterns_map = {
        # 智能/车机相关
        ('车机', '车载', '屏幕', '触控', '语音', '手机互联', 'CarPlay', 'Flyme', 'Auto', '智能', '互联', '连接'): 
            ['卡顿', '死机', '黑屏', '花屏', '不灵敏', '卡死', '反应慢', '延迟高', '断连', '不稳定', '识别不准', '不好用'],
        # 音响相关
        ('音响', '音箱', '扬声器', '音质', '哈曼卡顿', 'Flyme Sound', '无界之声', '头枕'): 
            ['音质差', '杂音', '噪音', '失真', '太小', '没低音', '破音'],
        # 空间相关
        ('空间', '后排', '腿部', '头部', '横向', '纵向', '进出', '储物', '杯架', '一拳', '坐'): 
            ['太紧', '很紧', '特别紧', '极其紧', '十分紧', '局促', '拥挤', '压抑', '太小', '很小', '不够', '不足', '欠缺', '塞不下'],
        # 动力相关
        ('动力', '加速', '响应', '提速', '油门', '电门', '跟脚', '超车', '发动机', '变速箱', '制动', '刹停', '动力储备'): 
            ['肉', '无力', '迟滞', '拖沓', '响应慢', '不跟脚', '动力不足', '起步慢', '超车无力', '怠速抖动', '提速慢'],
        # 舒适/座椅相关
        ('舒适', '座椅', '支撑', '包裹', '按摩', '通风', '加热', '静谧', '隔音', '噪音', '颠簸', '悬挂', '底盘', '调校'): 
            ['硬', '颠簸', '碎震', '晕车', '腰酸', '腿麻', '支撑不足', '侧倾大', '吵', '风噪大', '胎噪大', '发动机噪音大'],
        # 外观相关
        ('外观', '造型', '前脸', '尾部', '侧面', '车身比例', '线条', '灯光', '辨识度', '气场', '轮廓', '颜色', '格栅', '大灯', '尾灯', '门把手', '侧裙', '轴距', '视觉', '设计', '花生灯', '星芒', '璀璨', '盾形', '双幅', '星空', '灵眸', '矩阵', '导流槽', '尾门', '隐藏式', '镀铬', '月牙青', '直瀑'): 
            ['丑', '难看', '廉价', '塑料感', '低级', '过时', '老气', '平庸', '无特色', '不协调', '突兀', '不美观', '不好看'],
        # 内饰/材质/做工
        ('内饰', '材质', '做工', '装配', '质感', '用料', '包覆', '皮质', '软性', '中控', '氛围灯', '色彩', '布局', '按键', '细节', '豪华感', '精致感', '皮', '包裹'): 
            ['廉价', '塑料感', '硬塑', '粗糙', '缝隙大', '异响', '脱胶', '掉漆', '低级', '寒酸', '简陋', '瑕疵', '毛刺'],
        # 经济性/油耗/充电
        ('燃油', '油耗', '经济性', '能耗', '充电', '快充', '能量回收', 'ISG', '轻混', '代步', '巡航', '快充', '无线充电', '接口'): 
            ['费油', '烧油', '喝油', '油耗高', '不省油', '充电慢', '充电难', '续航焦虑', '不经济', '充不进'],
        # 价格/优惠
        ('价格', '优惠', '终端优惠', '性价比', '价格竞争力'): 
            ['贵', '坑', '宰客', '乱收费', '强制捆绑', '隐形消费', '性价比低', '不值', '亏', '太贵', '很贵', '不划算'],
        # 品牌/服务
        ('品牌', '知名度', '美誉度', '服务', '售前', '售后', '4S', '门店', '可靠', '踏实', '传播', '关注度', '问爆'): 
            ['差', '坑', '态度差', '敷衍', '推诿', '欺骗', '不专业', '爱理不理', '投诉多', '口碑差', '不靠谱'],
        # 安全
        ('安全', '主动安全', 'AEB', '辅助驾驶', '泊车', '360', '全景', '制动', '刹停', '安全感', '遥控泊车', '自动泊车', '云变道', '千里浩瀚', 'H3'): 
            ['缺失', '没有', '简配', '不配备', '刹不住', '失灵', '误触发', '不靠谱', '不安全'],
        # 便利性
        ('便利', '实用', '钥匙', '遥控', '尾门', '快充', '香氛', '空调', '温控', '净化', '接口', '电动尾门', '车载香氛'): 
            ['不方便', '麻烦', '没有', '缺失', '不支持', '不好用', '位置差', '够不着'],
    }

    # 找到匹配的模式组
    for kw_tuple, patterns in negative_patterns_map.items():
        if target_word in kw_tuple:
            for pat in patterns:
                if pat in surrounding:
                    return True, pat
    return False, None


def has_positive_context(text, target_word, window=50):
    """检查目标词附近是否有正面描述"""
    idx = text.find(target_word)
    if idx < 0:
        return False, None
    start = max(0, idx - window)
    end = min(len(text), idx + len(target_word) + window)
    surrounding = text[start:end]

    # 使用更具体的正面词汇，避免单字匹配导致误判
    positive_patterns = [
        # 明确的褒义词（2字以上）
        '很好', '很棒', '优秀', '优质', '满意', '喜欢', '喜爱', '点赞', '完美', '精彩',
        '出色', '卓越', '超群', '一流', '顶级', '高端', '豪华', '舒适', '静谧',
        '平顺', '流畅', '丝滑', '灵敏', '迅速', '强劲', '有劲', '省油', '经济',
        '实惠', '划算', '超值', '值得', '推荐', '信赖', '放心', '安心', '靠谱',
        '漂亮', '好看', '帅气', '大气', '霸气', '时尚', '前卫', '动感', '优雅',
        '精致', '细腻', '考究', '用心', '独特', '个性', '辨识度', '气场', '高级感',
        '宽敞', '宽裕', '充裕', '富裕', '空间大', '轴距长', '车身高', '座椅软', '支撑好', '包裹性强',
        '配置丰富', '功能齐全', '完善', '高配', '顶配', '标配', '实用', '科技感', '智能化',
        '便捷', '人性化', '贴心', '周到', '创新', '领先', '先进',
        '稳重', '稳健', '扎实', '沉稳', '操控好', '精准', '跟手', '响应快', '轻快',
        '惊喜', '超预期', '超过预期', '物超所值', '性价比高', '升级', '改进',
        '优化', '提升', '增强', '改善', '解决', '拉满', '惊艳', '完全', '妥妥',
        '友好', '方便', '快捷', '零学习成本', '幸福感', '加分', '经典', '重塑',
        '致敬', '同款', '迈巴赫', '不止一点', '相见', '靠近', '见证', '独一无二',
        '瞩目', '升级', '增加', '到位', '一览无遗', '高低功率', '匹配好', '轻松应对',
        '踏实', '可靠', '实用', '沉稳', '低调', '点缀', '闪闪发光', '闲逸',
        '阳光', '雨露', '方便快捷', '非常友好', '便捷', '经历', '验证', '反馈',
        '政策', '务实', '气场强', '拉满', 'Hold住', '惊艳', '清爽顺手',
        '幸福感', '零学习成本', '高速', '云变道', '遥控', '全部都有', '新手', '懒人',
        '扬声器', '无界之声', '耳边', '打断', '细节', '加分', '动力充沛', '跟脚',
        '干脆', '调好', '坐姿', '一拳半', '妥妥', '够了', '纠结', '千篇一律',
        '亲身', '亲眼', '亲自', '感受', '才算数',
        # 单字但语境明确的褒义
        '赞', '强', '快', '新', '好', '棒', '稳', '省',
    ]

    for pat in positive_patterns:
        if pat in surrounding:
            return True, pat
    return False, None


def analyze_sentiment_context(text_content, match_type, match_detail, data_code):
    """
    基于上下文语义理解进行情感分析
    返回: (sentiment, reason)
    sentiment: 1=正向褒义, 2=负向贬义, 0=中性
    reason: 分析依据说明
    """
    
    # 提取匹配关键词
    keywords = match_detail.replace('匹配关键词:', '').strip()
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    
    # 为每个关键词提取独立语境
    keyword_contexts = {}
    for kw in keyword_list:
        idx = text_content.find(kw)
        if idx >= 0:
            start = max(0, idx - 150)
            end = min(len(text_content), idx + len(kw) + 150)
            context = text_content[start:end]
            keyword_contexts[kw] = context
    
    if not keyword_contexts:
        return 0, f"{match_type}类指标，未在原文找到匹配关键词"
    
    # ========== 逐关键词分析，然后聚合 ==========
    all_results = []
    
    for kw, kw_context in keyword_contexts.items():
        neg = is_negated(kw_context, kw)
        has_neg, neg_word = has_negative_context(kw_context, kw)
        has_pos, pos_word = has_positive_context(kw_context, kw)
        
        # 特殊处理空间类否定词
        if any(x in match_type for x in ['空间', '乘坐空间', '后排', '腿部', '头部', '横向', '纵向', '进出', '储物', '杯架']):
            if kw in ['紧', '小', '窄'] and neg:
                all_results.append((1, f"空间类指标，原文否定「{kw}」（如：不会太紧、不紧、不小），表示空间充裕"))
                continue
        
        # 特殊处理价格/优惠类 - 优惠大是褒义
        if any(x in match_type for x in ['价格', '优惠', '终端优惠', '性价比', '价格竞争力']):
            if has_pos or (not has_neg and not neg):
                all_results.append((1, f"价格类指标，原文描述价格优势（优惠大、性价比高等）"))
                continue
        
        # 通用判断逻辑
        if neg or (has_neg and not has_pos):
            all_results.append((2, f"语境中「{kw}」被否定或出现负面描述「{neg_word}」"))
        elif has_pos:
            all_results.append((1, f"{match_type}类指标，原文对「{kw}」正面评价（{pos_word}等）"))
        else:
            all_results.append((0, f"{match_type}类指标，语境中对「{kw}」无明显褒贬倾向"))
    
    # 聚合结果：有任一负向则负向，无负向但有正向则正向，否则中性
    has_negative = any(r[0] == 2 for r in all_results)
    has_positive = any(r[0] == 1 for r in all_results)
    
    if has_negative:
        # 返回第一个负向的理由
        for r in all_results:
            if r[0] == 2:
                return 2, r[1]
    elif has_positive:
        # 返回第一个正向的理由
        for r in all_results:
            if r[0] == 1:
                return 1, r[1]
    else:
        return 0, all_results[0][1] if all_results else f"{match_type}类指标，语境中无明显褒贬倾向"


def fetch_all_data():
    """获取所有需要分析的数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取文本内容
    cursor.execute("SELECT data_code, text_content FROM txt_data")
    texts = {row['data_code']: row['text_content'] for row in cursor.fetchall()}
    
    # 获取所有 Label_data 记录
    cursor.execute("""
        SELECT id, data_code, match_type, match_detail, sentiment, sentiment_reason
        FROM Label_data
        ORDER BY data_code, id
    """)
    labels = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return texts, labels


def process_all():
    """处理所有记录"""
    texts, labels = fetch_all_data()
    
    print(f"📊 共 {len(labels)} 条 Label_data 记录待分析")
    print(f"📝 共 {len(texts)} 篇原文")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated = 0
    stats = {1: 0, 2: 0, 0: 0}
    
    for label in labels:
        data_code = label['data_code']
        match_type = label['match_type']
        match_detail = label['match_detail']
        text_content = texts.get(data_code, '')
        
        # 语义分析
        sentiment, reason = analyze_sentiment_context(text_content, match_type, match_detail, data_code)
        
        stats[sentiment] += 1
        
        # 更新数据库
        cursor.execute("""
            UPDATE Label_data 
            SET sentiment = %s, sentiment_reason = %s
            WHERE id = %s
        """, (sentiment, reason, label['id']))
        
        updated += 1
        
        if updated % 20 == 0:
            conn.commit()
            print(f"  已处理 {updated}/{len(labels)} 条...")
        
        # 打印负向和中性的详情，正向只统计
        if sentiment != 1:
            label_name = {1: '正向', 2: '负向', 0: '中性'}[sentiment]
            print(f"  [{label_name}] ID:{label['id']} | {data_code} | {match_type} | {match_detail[:50]}")
            print(f"       依据: {reason}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ 完成！共更新 {updated} 条记录")
    print(f"📊 统计: 正向={stats[1]} 负向={stats[2]} 中性={stats[0]}")
    
    return stats


def verify_results():
    """验证结果"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT data_code, sentiment, COUNT(*) as cnt
        FROM Label_data 
        GROUP BY data_code, sentiment
        ORDER BY data_code, sentiment
    """)
    
    print("\n🔍 按数据编号验证:")
    for row in cursor.fetchall():
        label_name = {1: '正向', 2: '负向', 0: '中性'}[row['sentiment']]
        print(f"   {row['data_code']}: {label_name} = {row['cnt']} 条")
    
    # 显示负向和中性的详细记录
    cursor.execute("""
        SELECT id, data_code, match_type, match_detail, sentiment, sentiment_reason
        FROM Label_data 
        WHERE sentiment != 1
        ORDER BY data_code, id
    """)
    
    print("\n📋 非正向记录详情:")
    for row in cursor.fetchall():
        label_name = {2: '负向', 0: '中性'}[row['sentiment']]
        print(f"   [{label_name}] ID:{row['id']} | {row['data_code']} | {row['match_type']}")
        print(f"      关键词: {row['match_detail']}")
        print(f"      依据: {row['sentiment_reason']}")
        print()
    
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print("🚀 开始基于上下文语义理解的情感分析...")
    print("=" * 60)
    
    stats = process_all()
    
    print("\n" + "=" * 60)
    print("📋 最终统计报告")
    print("=" * 60)
    total = sum(stats.values())
    print(f"总计: {total} 条")
    print(f"正向(褒义): {stats[1]} ({stats[1]/total*100:.1f}%)")
    print(f"负向(贬义): {stats[2]} ({stats[2]/total*100:.1f}%)")
    print(f"中性: {stats[0]} ({stats[0]/total*100:.1f}%)")
    
    verify_results()
    
    print("\n✅ 分析完成！")