"""TianYuan (天元农历) - Ziwu Liuzhu & Linggui Bafa Engine."""
from __future__ import annotations

from datetime import datetime
from lunar_python import Lunar

# 1. 穴位详细手册
ACUPOINT_DETAILS = {
    '足窍阴': {'weiZhi': '足第4趾末节外侧，趾甲角旁0.1寸', 'gongNeng': '治疗头痛、目赤肿痛、失眠', 'fangFa': '浅刺0.1寸或点刺出血'},
    '行间': {'weiZhi': '足背第1, 2趾间，趾蹼缘后方赤白肉际处', 'gongNeng': '治疗头痛、目眩、月经不调', 'fangFa': '直刺0.5-0.8寸'},
    '少泽': {'weiZhi': '小指末节尺侧，指甲角旁0.1寸', 'gongNeng': '治疗头痛、咽喉肿痛、乳腺炎', 'fangFa': '浅刺0.1寸或点刺出血'},
    '少冲': {'weiZhi': '小指末节桡侧，指甲角旁0.1寸', 'gongNeng': '治疗心悸、心痛、癫狂', 'fangFa': '浅刺0.1寸或点刺出血'},
    '厉兑': {'weiZhi': '足第2趾末节外侧，趾甲角旁0.1寸', 'gongNeng': '治疗牙痛、鼻衄、癫狂', 'fangFa': '浅刺0.1寸'},
    '隐白': {'weiZhi': '足大趾末节内侧，趾甲角旁0.1寸', 'gongNeng': '治疗月经过多、腹胀、便血', 'fangFa': '浅刺0.1寸'},
    '商阳': {'weiZhi': '食指末节桡侧，指甲角旁0.1寸', 'gongNeng': '治疗咽喉肿痛、牙痛、热病', 'fangFa': '浅刺0.1寸或点刺出血'},
    '少商': {'weiZhi': '拇指末节桡侧，指甲角旁0.1寸', 'gongNeng': '治疗咽喉肿痛、咳嗽、发热', 'fangFa': '浅刺0.1寸或点刺出血'},
    '至阴': {'weiZhi': '足小趾末节外侧，趾甲角旁0.1寸', 'gongNeng': '治疗头痛、胎位不正、难产', 'fangFa': '浅刺0.1寸'},
    '涌泉': {'weiZhi': '足底部，蜷足时足前部凹陷处', 'gongNeng': '治疗头痛、眩晕、失眠', 'fangFa': '直刺0.5-1寸'},
    '太渊': {'weiZhi': '腕掌侧横纹桡侧，桡动脉搏动处', 'gongNeng': '治疗咳嗽、气喘、胸痛', 'fangFa': '直刺0.3-0.5寸，避开桡动脉'},
    '曲池': {'weiZhi': '肘横纹外侧端，屈肘时尺泽与肱骨外上髁连线中点', 'gongNeng': '治疗热病、咽喉肿痛、手臂肿痛', 'fangFa': '直刺1-1.5寸'},
    '足三里': {'weiZhi': '小腿外侧，犊鼻下3寸，距胫骨前缘1横指', 'gongNeng': '治疗胃痛、呕吐、消化不良', 'fangFa': '直刺1-2寸'},
    '太白': {'weiZhi': '足内侧缘，第1跖骨小头后下方凹陷处', 'gongNeng': '治疗胃痛、腹胀、泄泻', 'fangFa': '直刺0.5-0.8寸'},
    '中冲': {'weiZhi': '手中指末节尖端中央', 'gongNeng': '治疗中风昏迷、中暑、小儿惊风', 'fangFa': '浅刺0.1寸或点刺出血'},
    '关冲': {'weiZhi': '手无名指末节尺侧，指甲角旁0.1寸', 'gongNeng': '治疗头痛、目赤、咽喉肿痛', 'fangFa': '浅刺0.1寸或点刺出血'},
    '申脉': {'weiZhi': '足外侧部，外踝直下方凹陷中', 'gongNeng': '治疗头痛、眩晕、失眠、癫痫', 'fangFa': '直刺0.3-0.5寸，可灸'},
    '照海': {'weiZhi': '足内侧，内踝尖下方凹陷处', 'gongNeng': '治疗咽喉痛、失眠、月经不调', 'fangFa': '直刺0.5-0.8寸，可灸'},
    '外关': {'weiZhi': '前臂背侧，阳池与肘尖连线上，腕背横纹上2寸', 'gongNeng': '治疗头痛、耳聋、上肢痹痛', 'fangFa': '直刺0.5-1寸，可灸'},
    '足临泣': {'weiZhi': '足背外侧，第4, 5跖骨结合部前方凹陷处', 'gongNeng': '治疗目眩、胁痛、月经不调', 'fangFa': '直刺0.3-0.5寸，可灸'},
    '公孙': {'weiZhi': '足内侧缘，第1跖骨基底前下方', 'gongNeng': '治疗胃痛、呕吐、腹痛', 'fangFa': '直刺0.6-1.2寸，可灸'},
    '后溪': {'weiZhi': '手掌尺侧，第5掌指关节后尺侧近端掌横纹头赤白肉际', 'gongNeng': '治疗头痛、腰背痛、目赤', 'fangFa': '直刺0.5-1寸，可灸'},
    '内关': {'weiZhi': '前臂掌侧，腕横纹上2寸，掌长肌腱与桡侧腕屈肌腱之间', 'gongNeng': '治疗心痛、心悸、胃痛', 'fangFa': '直刺0.5-1寸，可灸'},
    '列缺': {'weiZhi': '前臂桡侧缘，桡骨茎突上方，腕横纹上1.5寸', 'gongNeng': '治疗咳嗽、气喘、头痛', 'fangFa': '向上斜刺0.3-0.5寸，可灸'}
}

class ZiwuLiuzhu:
    """子午流注与灵龟八法计算引擎."""

    @staticmethod
    def calculate_najia(lunar: Lunar) -> dict:
        """子午流注纳甲法计算."""
        # 修正方法名：getDayInGanZhi, getTimeInGanZhi
        ri_gan = lunar.getDayGan()
        shi_gan = lunar.getTimeGan()
        shi_chen = lunar.getTimeZhi()
        
        zhi_ri_map = {'甲':'胆经','乙':'肝经','丙':'小肠经','丁':'心经','戊':'胃经','己':'脾经','庚':'大肠经','辛':'肺经','壬':'膀胱经','癸':'肾经'}
        kai_xue_map = {
            '甲': {'xue': '足窍阴', 'shu': '井穴', 'jing': '胆经', 'wu': '金'},
            '乙': {'xue': '行间', 'shu': '荥穴', 'jing': '肝经', 'wu': '火'},
            '丙': {'xue': '少泽', 'shu': '井穴', 'jing': '小肠经', 'wu': '金'},
            '丁': {'xue': '少冲', 'shu': '井穴', 'jing': '心经', 'wu': '木'},
            '戊': {'xue': '厉兑', 'shu': '井穴', 'jing': '胃经', 'wu': '金'},
            '己': {'xue': '隐白', 'shu': '井穴', 'jing': '脾经', 'wu': '木'},
            '庚': {'xue': '商阳', 'shu': '井穴', 'jing': '大肠经', 'wu': '金'},
            '辛': {'xue': '少商', 'shu': '井穴', 'jing': '肺经', 'wu': '木'},
            '壬': {'xue': '至阴', 'shu': '井穴', 'jing': '膀胱经', 'wu': '金'},
            '癸': {'xue': '涌泉', 'shu': '井穴', 'jing': '肾经', 'wu': '木'}
        }
        
        info = kai_xue_map.get(shi_gan, {'xue':'休息','shu':'-','jing':'-','wu':'-'})
        detail = ACUPOINT_DETAILS.get(info['xue'], {})
        
        # 修正点：使用 getDayInGanZhi() 和 getTimeInGanZhi()
        miao_shu = f"{lunar.getDayInGanZhi()}日{lunar.getTimeInGanZhi()}时（{shi_chen}时）"
        zhi_ri_jing = zhi_ri_map.get(ri_gan, "未知")
        summary = f"子午流注开穴：{info['xue']} ({info['shu']}, {info['jing']})"

        return {
            "zhi_ri_jing": zhi_ri_jing,
            "xuewei": info['xue'],
            "shuxing": info['shu'],
            "jingluo": info['jing'],
            "wuxing": info['wu'],
            "weizhi": detail.get('weiZhi', "未知"),
            "gongneng": detail.get('gongNeng', "未知"),
            "fangfa": detail.get('fangFa', "未知"),
            "miaoshu": miao_shu,
            "xiangximiaoshu": f"{miao_shu}，值日经：{zhi_ri_jing}，{summary}。\n穴位位置：{detail.get('weiZhi', '未知')}\n主要功能：{detail.get('gongNeng', '未知')}\n针刺方法：{detail.get('fangFa', '未知')}",
            "summary": summary
        }

    @staticmethod
    def calculate_linggui(lunar: Lunar, gender: str) -> dict:
        """灵龟八法计算."""
        tg_map = {'甲': 9, '己': 9, '乙': 8, '庚': 8, '丙': 7, '辛': 7, '丁': 6, '壬': 6, '戊': 5, '癸': 5}
        dz_map = {'子': 9, '午': 9, '丑': 8, '未': 8, '寅': 7, '申': 7, '卯': 6, '酉': 6, '辰': 5, '戌': 5, '巳': 4, '亥': 4}
        
        zong_he = tg_map.get(lunar.getDayGan(), 0) + dz_map.get(lunar.getDayZhi(), 0) + \
                  tg_map.get(lunar.getTimeGan(), 0) + dz_map.get(lunar.getTimeZhi(), 0)
        
        is_yang_ri = lunar.getDayGan() in ['甲', '丙', '戊', '庚', '壬']
        chu_shu = 9 if is_yang_ri else 6
        yu_shu = zong_he % chu_shu or chu_shu
        
        if yu_shu == 5:
            yu_shu = 2 if gender == "男" else 8
            
        xue_wei_map = {
            1: {'xue': '申脉', 'jing': '阳跷脉', 'gua': '坎', 'gong': '坎一宫'},
            2: {'xue': '照海', 'jing': '阴跷脉', 'gua': '坤', 'gong': '坤二宫'},
            3: {'xue': '外关', 'jing': '阳维脉', 'gua': '震', 'gong': '震三宫'},
            4: {'xue': '足临泣', 'jing': '带脉', 'gua': '巽', 'gong': '巽四宫'},
            6: {'xue': '公孙', 'jing': '冲脉', 'gua': '乾', 'gong': '乾六宫'},
            7: {'xue': '后溪', 'jing': '督脉', 'gua': '兑', 'gong': '兑七宫'},
            8: {'xue': '内关', 'jing': '阴维脉', 'gua': '艮', 'gong': '艮八宫'},
            9: {'xue': '列缺', 'jing': '任脉', 'gua': '离', 'gong': '离九宫'}
        }
        
        res = xue_wei_map.get(yu_shu, {'xue':'未知','jing':'未知','gua':'未知','gong':'未知'})
        detail = ACUPOINT_DETAILS.get(res['xue'], {})
        
        # 修正点：使用 getDayInGanZhi() 和 getTimeInGanZhi()
        miao_shu = f"{lunar.getDayInGanZhi()}日{lunar.getTimeInGanZhi()}时（{lunar.getTimeZhi()}时时）"
        summary = f"灵龟八法取穴：{res['xue']} ({res['jing']})，对应{res['gong']}"
        
        return {
            "xuewei": res['xue'],
            "jingluo": res['jing'],
            "gua": res['gua'],
            "gongwei": res['gong'],
            "weizhi": detail.get('weiZhi', "未知"),
            "gongneng": detail.get('gongNeng', "未知"),
            "fangfa": detail.get('fangFa', "未知"),
            "miaoshu": miao_shu,
            "xiangximiaoshu": f"{miao_shu}，{summary}。\n穴位位置：{detail.get('weiZhi', '未知')}\n主要功能：{detail.get('gongNeng', '未知')}\n针刺方法：{detail.get('fangFa', '未知')}",
            "summary": summary
        }

    @staticmethod
    def calculate_nazi(tst_dt: datetime) -> dict:
        """子午流注纳子法计算."""
        shi_chen_map = {
            '子': {'jing': '胆经', 'xue': '足窍阴', 'shu': '井穴', 'time': '23:00-01:00'},
            '丑': {'jing': '肝经', 'xue': '行间', 'shu': '荥穴', 'time': '01:00-03:00'},
            '寅': {'jing': '肺经', 'xue': '太渊', 'shu': '输穴', 'time': '03:00-05:00'},
            '卯': {'jing': '大肠经', 'xue': '曲池', 'shu': '合穴', 'time': '05:00-07:00'},
            '辰': {'jing': '胃经', 'xue': '足三里', 'shu': '合穴', 'time': '07:00-09:00'},
            '巳': {'jing': '脾经', 'xue': '太白', 'shu': '输穴', 'time': '09:00-11:00'},
            '午': {'jing': '心经', 'xue': '少冲', 'shu': '井穴', 'time': '11:00-13:00'},
            '未': {'jing': '小肠经', 'xue': '后溪', 'shu': '输穴', 'time': '13:00-15:00'},
            '申': {'jing': '膀胱经', 'xue': '至阴', 'shu': '井穴', 'time': '15:00-17:00'},
            '酉': {'jing': '肾经', 'xue': '涌泉', 'shu': '井穴', 'time': '17:00-19:00'},
            '戌': {'jing': '心包经', 'xue': '中冲', 'shu': '井穴', 'time': '19:00-21:00'},
            '亥': {'jing': '三焦经', 'xue': '关冲', 'shu': '井穴', 'time': '21:00-23:00'}
        }
        
        hour = tst_dt.hour
        branches = ["子","丑","丑","寅","寅","卯","卯","辰","辰","巳","巳","午","午","未","未","申","申","酉","酉","戌","戌","亥","亥","子"]
        di_zhi = branches[hour]
        
        info = shi_chen_map.get(di_zhi, {})
        detail = ACUPOINT_DETAILS.get(info.get('xue'), {})
        
        miao_shu = f"{di_zhi}时（{info.get('time', '未知')}）"
        summary = f"子午流注纳子法：{di_zhi}时当令{info.get('jing')}，取穴{info.get('xue')} ({info.get('shu')})"
        
        return {
            "jingluo": info.get('jing'),
            "xuewei": info.get('xue'),
            "shuxing": info.get('shu'),
            "shijian": info.get('time'),
            "weizhi": detail.get('weiZhi', "未知"),
            "gongneng": detail.get('gongNeng', "未知"),
            "fangfa": detail.get('fangFa', "未知"),
            "miaoshu": miao_shu,
            "xiangximiaoshu": f"{miao_shu}，气血流注{info.get('jing')}，当取{info.get('shu')}穴{info.get('xue')}。\n穴位位置：{detail.get('weiZhi', '未知')}\n主要功能：{detail.get('gongNeng', '未知')}\n针刺方法：{detail.get('fangFa', '未知')}",
            "summary": summary
        }
