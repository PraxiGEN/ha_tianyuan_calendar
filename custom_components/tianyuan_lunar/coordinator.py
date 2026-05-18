"""TianYuan (天元农历) 核心协调器."""
# 干支纪日：晚子时日柱算当天
# 干支纪年：新年以立春节气交接的时刻起算
from __future__ import annotations

import math
import logging
from datetime import datetime, date, timedelta
from typing import Any, TypedDict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

# 导入外部算法库和工具类
from .tianyuanshushu import ZiwuLiuzhu, TianYuanShuShu, IchingLibrary
from .const import (
    DOMAIN, 
    LOGGER,
    CONF_REFRESH_INTERVAL, 
    CONF_CUSTOM_LONGITUDE,
    CONF_ENABLE_SHUSHU,
    CONF_CALC_MODE,
    MODE_ST,
    MODE_TST,
    KEY_SHUSHU_DATA,
    SHUSHU_MEIHUA_GUA,
    SHUSHU_HUANGJI_GUA
)

# 导入农历库
from lunar_python import Lunar, Solar, LunarTime
from lunar_python.util import HolidayUtil

class TianYuanData(TypedDict):
    """协调器数据结构定义."""
    lunar: Lunar
    solar: Solar
    tst_dt: datetime
    is_realtime: bool
    gender: str
    holiday_data: dict[str, Any]
    term_data: dict[str, Any]
    shichen_data: dict[str, Any]
    full_attributes: dict[str, Any]
    linggui: dict[str, Any]
    najia: dict[str, Any]
    nazi: dict[str, Any]

class TianYuanCoordinator(DataUpdateCoordinator[TianYuanData]):
    """天元核心计算协调器."""

    def __init__(self, hass: HomeAssistant, entry, version: str) -> None:
        """初始化协调器."""
        self.entry = entry
        self.version = version
        self.view_date: date | None = None
        self.gender: str = "男"
        self.selected_iching = None
        
        refresh_min = entry.options.get(CONF_REFRESH_INTERVAL, 1)
        
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=refresh_min),
        )

    @property
    def device_info(self):
        """定义设备模型."""
        from homeassistant.helpers.entity import DeviceInfo
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="TianYuan Lunar",
            manufacturer="TianYuan Lunar",
            sw_version=str(self.version),
            entry_type="service",
            configuration_url="https://github.com/hzonz/tianyuan_lunar",
        )
        
    @property
    def shushu_device_info(self):
        """子设备：天元术数."""
        from homeassistant.helpers.entity import DeviceInfo
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.entry.entry_id}_shushu")}, # 独立的设备 ID
            name="TianYuan ShuShu",
            manufacturer="TianYuan ShuShu",
            sw_version=str(self.version),
            entry_type="service",
            via_device=(DOMAIN, self.entry.entry_id),
        )        

    def _calculate_tst(self, dt: datetime, lon: float) -> datetime:
        """计算真太阳时 (True Solar Time)."""
        lon_offset = (lon - 120) * 4
        day_of_year = dt.timetuple().tm_yday
        b = 2 * math.pi * (day_of_year - 81) / 365
        eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
        return dt + timedelta(minutes=lon_offset + eot)

    async def _async_update_data(self) -> TianYuanData:
        """主计算任务：将同步逻辑委托给线程池."""
        return await self.hass.async_add_executor_job(self._get_sync_data)

    def _get_sync_data(self) -> TianYuanData:
        now = dt_util.now()
        is_realtime = self.view_date is None
    
        calc_base = (
            now if is_realtime
            else datetime.combine(self.view_date, now.time()).replace(tzinfo=now.tzinfo)
        )
    
        # 计算真太阳时
        lon = float(self.entry.options.get(CONF_CUSTOM_LONGITUDE, 120.0))
        tst_dt = self._calculate_tst(calc_base, lon)
    
        # 创建历法宇宙
        st_lunar = Lunar.fromDate(calc_base)
        tst_lunar = Lunar.fromDate(tst_dt)
        solar = Solar.fromDate(tst_dt)
    
        # 模式选择
        calc_mode = self.entry.options.get(CONF_CALC_MODE, MODE_ST)
        general_lunar = tst_lunar if calc_mode == MODE_TST else st_lunar
    
        # 构建基础数据
        data: TianYuanData = {
            "lunar": general_lunar,
            "solar": solar,
            "tst_dt": tst_dt,
            "is_realtime": is_realtime,
            "gender": self.gender,
            "holiday_data": self._get_holiday_logic(st_lunar, solar, calc_base),
            "term_data": self._get_term_logic(st_lunar, solar),
            "shichen_data": self._get_shichen_logic(st_lunar, calc_base),
            "full_attributes": self._get_full_attributes(general_lunar, solar),
            "more_entities_data": self._get_more_logic(tst_lunar, tst_dt),
            # 术数占位符
            "najia": {}, "linggui": {}, "nazi": {},
            "xlr_info": {},  "iching_info": {}, "iching_display_name": "",
            KEY_SHUSHU_DATA: {}
        }
    
        # 只有开启开关才执行深度计算
        if self.entry.options.get(CONF_ENABLE_SHUSHU):
            shushu_results = self._build_shushu(tst_lunar, tst_dt, solar)
            data.update(shushu_results)
    
        return data

    def _build_shushu(self, tst_lunar, tst_dt, solar):
        """构建天元术数."""
        # 小六壬
        xlr_data = TianYuanShuShu.get_xiao_liu_ren(tst_lunar)
        # 梅花易数
        meihua_gua = TianYuanShuShu.get_meihua_gua(tst_lunar)
        # 皇极经世
        huangji_gua = TianYuanShuShu.get_huangji_context(tst_lunar, solar)
    
        target_gua = self.selected_iching or meihua_gua.get("state")
        
        gua_detail = IchingLibrary.get_gua(target_gua)
    
        return {

            "najia": ZiwuLiuzhu.calculate_najia(tst_lunar),
            "linggui": ZiwuLiuzhu.calculate_linggui(tst_lunar, self.gender),
            "nazi": ZiwuLiuzhu.calculate_nazi(tst_dt),
            
            KEY_SHUSHU_DATA: {
                SHUSHU_MEIHUA_GUA: meihua_gua,
                SHUSHU_HUANGJI_GUA: huangji_gua,
            },
            "xlr_info": xlr_data,
            "iching_display_name": target_gua, 
            "iching_info": gua_detail
        }


    def _get_holiday_logic(self, lunar, solar, dt):
        """假期."""
        h = HolidayUtil.getHoliday(dt.year, dt.month, dt.day)
        state = "工作日" if h is None or h.isWork() else h.getName()
        
        festivals = []
        for i in range(-42, 43):
            if i == 0: continue
            d_s = solar.next(i)
            d_l = lunar.next(i)
            d_h = HolidayUtil.getHoliday(d_s.getYear(), d_s.getMonth(), d_s.getDay())
            if d_h and not d_h.isWork():
                festivals.append({"name": d_h.getName(), "days": i, "date": d_s.toYmd(), "type": "法定假期"})
            for f in d_s.getFestivals():
                festivals.append({"name": f, "days": i, "date": d_s.toYmd(), "type": "阳历节日"})
            for f in d_l.getFestivals():
                festivals.append({"name": f, "days": i, "date": d_l.getSolar().toYmd(), "type": "农历节日"})

        return {
            "state": state,
            "当天节日": {"阳历节日": solar.getFestivals() or ["无阳历节日"], "农历节日": lunar.getFestivals() or ["无农历节日"]},
            "假期信息": {"名称": h.getName() if h else "无假期", "类型": "法定节假日" if h and not h.isWork() else "工作日", "是否工作日": "是" if (h is None or h.isWork()) else "否"},
            "最近节日": sorted(festivals, key=lambda x: abs(x['days']))[:10]
        }

    def _get_term_logic(self, lunar, solar):
        """节气."""
        curr = lunar.getCurrentJieQi()
        next_jq = lunar.getNextJieQi()
        prev = lunar.getPrevJieQi()
        target_dt = datetime.strptime(next_jq.getSolar().toYmd(), "%Y-%m-%d")
        curr_dt = datetime.strptime(solar.toYmd(), "%Y-%m-%d")
        diff = (target_dt - curr_dt).days
        state = f"今天是{curr.getName()}" if curr else f"{diff}天后是{next_jq.getName()}"
        return {
            "state": state,
            "上一节气": f"{prev.getName()} {prev.getSolar().toYmd()}",
            "下一节气": f"{next_jq.getName()} {next_jq.getSolar().toYmd()}"
        }

    def _get_shichen_logic(self, lunar, dt):
        """十二时辰."""
        # 1. 确定当前时辰状态 (例如: 酉时)
        current_shichen_state = f"{lunar.getTimeZhi()}时"

        # 2. 生成 13 个时辰的平铺字典 (用于属性)
        configs = [
            ("早子时", 0), ("丑时", 1), ("寅时", 3), ("卯时", 5), ("辰时", 7),
            ("巳时", 9), ("午时", 11), ("未时", 13), ("申时", 15),
            ("酉时", 17), ("戌时", 19), ("亥时", 21), ("晚子时", 23)
        ]

        shichen_results = {}
        for key, h in configs:
            lt = LunarTime.fromYmdHms(lunar.getYear(), lunar.getMonth(), lunar.getDay(), h, 0, 0)
            
            # 时间范围显示优化
            if key == "早子时":
                time_range = "00:00 - 00:59"
            elif key == "晚子时":
                time_range = "23:00 - 23:59"
            else:
                time_range = f"{lt.getMinHm()} - {lt.getMaxHm()}"

            shichen_results[key] = {
                "时间": time_range,
                "干支": lt.getGanZhi(),
                "十二天神": f"{lt.getTianShen()}({lt.getTianShenType()}) {lt.getTianShenLuck()}",
                "吉凶": lt.getTianShenLuck(),
                "冲煞": f"冲{lt.getChongDesc()} 煞{lt.getSha()}",
                "宜": ". ".join(lt.getYi()) if lt.getYi() else "无",
                "忌": ". ".join(lt.getJi()) if lt.getJi() else "无"
            }

        return {
            "state": current_shichen_state,
            "data": shichen_results
        }

    def _get_zodiac_relations(self, zhi: str) -> dict[str, str]:
        """计算地支生肖的动合关系 (冲、刑、害、破、三合、六合)."""
        # 地支对应的生肖关系表
        relation_map = {
            "子": {"六合": "牛", "三合": "猴 龙", "相冲": "马", "相刑": "兔", "相害": "羊", "相破": "鸡"},
            "丑": {"六合": "鼠", "三合": "蛇 鸡", "相冲": "羊", "相刑": "狗", "相害": "马", "相破": "龙"},
            "寅": {"六合": "猪", "三合": "马 狗", "相冲": "猴", "相刑": "蛇 猴", "相害": "蛇", "相破": "猪"},
            "卯": {"六合": "狗", "三合": "猪 羊", "相冲": "鸡", "相刑": "鼠", "相害": "龙", "相破": "马"},
            "辰": {"六合": "鸡", "三合": "猴 鼠", "相冲": "狗", "相刑": "龙(自刑)", "相害": "兔", "相破": "牛"},
            "巳": {"六合": "猴", "三合": "鸡 牛", "相冲": "猪", "相刑": "虎 猴", "相害": "虎", "相破": "猴"},
            "午": {"六合": "羊", "三合": "虎 狗", "相冲": "鼠", "相刑": "马(自刑)", "相害": "牛", "相破": "兔"},
            "未": {"六合": "马", "三合": "猪 兔", "相冲": "丑", "相刑": "狗 丑", "相害": "鼠", "相破": "狗"},
            "申": {"六合": "蛇", "三合": "鼠 龙", "相冲": "寅", "相刑": "虎 巳", "相害": "猪", "相破": "蛇"},
            "酉": {"六合": "龙", "三合": "蛇 牛", "相冲": "卯", "相刑": "酉(自刑)", "相害": "狗", "相破": "鼠"},
            "戌": {"六合": "兔", "三合": "虎 马", "相冲": "龙", "相刑": "牛 未", "相害": "鸡", "相破": "羊"},
            "亥": {"六合": "寅", "三合": "兔 羊", "相冲": "蛇", "相刑": "亥(自刑)", "相害": "猴", "相破": "虎"},
        }
        return relation_map.get(zhi, {
            "六合": "无", "三合": "无", "相冲": "无", 
            "相刑": "无", "相害": "无", "相破": "无"
        })

    async def async_set_iching_gua(self, name: str):
        """由 Select 实体调用"""
        self.selected_iching = name
        await self.async_refresh()


    def _get_more_logic(self, lunar, tst_dt):
        """更多实体."""
        
        ba_zi = lunar.getEightChar()
        
        gender_prefix = "乾造" if self.gender == "男" else "坤造"
        
        day_zhi = lunar.getDayZhiExact2()
        relations = self._get_zodiac_relations(day_zhi)
        
        return {
            # 真太阳时实体 (基于真太阳时的时辰属性)
            "tst_time": {
                "state": f"{lunar.getTimeZhi()}时",
                "attributes": {
                    "农历": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                    "八字": lunar.getEightChar().toString(),
                    "十二天神": f"{lunar.getTimeTianShen()}({lunar.getTimeTianShenType()}) {lunar.getTimeTianShenLuck()}",
                    "冲煞": f"冲{lunar.getTimeChongDesc()} 煞{lunar.getTimeSha()}",
                    "宜": ". ".join(lunar.getTimeYi()) if lunar.getTimeYi() else "无",
                    "忌": ". ".join(lunar.getTimeJi()) if lunar.getTimeJi() else "无",
                    "太阳时": tst_dt.strftime("%H:%M")
                }
            },
            
            # 八字实体
            "bazi": {
                "state": f"{gender_prefix} {ba_zi.toString()}",
                "attributes": {
                    "五行": f"{ba_zi.getYearWuXing()}, {ba_zi.getMonthWuXing()}, {ba_zi.getDayWuXing()}, {ba_zi.getTimeWuXing()}",
                    "纳音": f"{ba_zi.getYearNaYin()}, {ba_zi.getMonthNaYin()}, {ba_zi.getDayNaYin()}, {ba_zi.getTimeNaYin()}",
                    "十神": f"{ba_zi.getYearShiShenGan()}, {ba_zi.getMonthShiShenGan()}, {ba_zi.getDayShiShenGan()}, {ba_zi.getTimeShiShenGan()}",
                    "地势": f"{ba_zi.getYearDiShi()}, {ba_zi.getMonthDiShi()}, {ba_zi.getDayDiShi()}, {ba_zi.getTimeDiShi()}",
                    "其他": {
                        "胎元": ba_zi.getTaiYuan(),
                        "命宫": ba_zi.getMingGong(),
                        "身宫": ba_zi.getShenGong()
                    }
                }
            },
            
            # 天干地支实体
            "ganzhi": {
                "state": f"{lunar.getYearInGanZhiExact()}{lunar.getYearShengXiaoExact()}年 {lunar.getMonthInGanZhiExact()}月 {lunar.getDayInGanZhiExact()}日",
                "attributes": {
                    "干支": {
                        "年": f"{lunar.getYearInGanZhiExact()}年", 
                        "月": f"{lunar.getMonthInGanZhiExact()}月", 
                        "日": f"{lunar.getDayInGanZhiExact2()}日"
                    },
                    "纳音": {
                        "年": lunar.getYearNaYin(), 
                        "月": lunar.getMonthNaYin(), 
                        "日": lunar.getDayNaYin(),
                        "时": lunar.getTimeNaYin()
                    },
                    "生肖": {
                        "年": lunar.getYearShengXiaoExact(), 
                        "月": lunar.getMonthShengXiaoExact(), 
                        "日": lunar.getDayShengXiao(),
                        "时": lunar.getDayShengXiao()
                    }
                }
            },
            
            # 十二天神实体
            "twelve_gods": {
                "state": f"{lunar.getDayTianShen()}({lunar.getDayTianShenType()}) {lunar.getDayTianShenLuck()}",
                "attributes": {
                    "择日法": "青龙明堂与天刑，朱雀金贵天德神； 白虎玉堂天牢黑，玄武司命惊勾陈。",
                    "诀曰": "道远几时通达，路遥何日还乡。"
                }
            },
            
            # 冲煞实体
            "chongsha": {
                "state": f"{lunar.getDayShengXiao()}日 冲{lunar.getDayChongDesc()} 煞{lunar.getDaySha()}",
                "attributes": {
                    "当日生肖": lunar.getDayShengXiao(),
                    "六合": relations["六合"],
                    "三合": relations["三合"],
                    "相冲": relations["相冲"],
                    "相刑": relations["相刑"],
                    "相害": relations["相害"],
                    "相破": relations["相破"]
                }
            },
            
            # 星宿实体
            "xingxiu": {
                "state": f"{lunar.getGong()}方{lunar.getXiu()}{lunar.getZheng()}{lunar.getAnimal()}-{lunar.getXiuLuck()}",
                "attributes": {
                    "歌诀": lunar.getXiuSong()
                }
            }
            
            # 季节实体
            # "season": {
            #     "state": lunar.getSeason(),
            #     "attributes": {}
            # }
        }
    
    def _get_full_attributes(self, l: Lunar, s: Solar) -> dict[str, Any]:
        """构建全量农历属性字段 - 修复变量未定义错误."""
        # 1. 预先获取节气对象
        curr_jq = l.getCurrentJieQi()
        prev_jq = l.getPrevJieQi()
        next_jq = l.getNextJieQi()
        
        # 2. 预先计算节气差字符串
        target_dt = datetime.strptime(next_jq.getSolar().toYmd(), "%Y-%m-%d")
        current_dt = datetime.strptime(s.toYmd(), "%Y-%m-%d")
        diff_days = (target_dt - current_dt).days
        
        if curr_jq:
            jq_diff_str = f"今天是{curr_jq.getName()}"
        else:
            jq_diff_str = f"{diff_days}天后是{next_jq.getName()}"

        # 3. 返回完整的字典结构
        return {
            "solar": {
                "日期": s.toYmd(),
                "年月日": {"年": f"{s.getYear()}年", "月": f"{s.getMonth()}月", "日": f"{s.getDay()}日"},
                "星座": f"{s.getXingZuo()}座"
            },
            "lunar": {
                "农历": f"{l.getMonthInChinese()}月{l.getDayInChinese()}",
                "星期": f"星期{l.getWeekInChinese()}",
                "天干地支": f"{l.getYearInGanZhiExact()}{l.getYearShengXiaoExact()}年 {l.getMonthInGanZhiExact()}月 {l.getDayInGanZhiExact2()}日",
                # "年干支": f"{l.getYearInGanZhiExact()}{l.getYearShengXiaoExact()}年",
                # "干支": {
                #     "年": f"{l.getYearInGanZhiExact()}年", 
                #     "月": f"{l.getMonthInGanZhiExact()}月", 
                #     "日": f"{l.getDayInGanZhiExact2()}日"
                # },
                "日禄": l.getDayLu(),
                # "生肖": {
                #     "年": l.getYearShengXiaoExact(), 
                #     "月": l.getMonthShengXiaoExact(), 
                #     "日": l.getDayShengXiao()
                # },
                # "节气": {
                #     "节气差": jq_diff_str,
                #     "上一节气": f"{prev_jq.getName()} {prev_jq.getSolar().toYmd()}",
                #     "下一节气": f"{next_jq.getName()} {next_jq.getSolar().toYmd()}"
                # },
                "物候": f"{l.getHou()} {l.getWuHou()}",
                "六曜": l.getLiuYao(),
                "东方星宿": f"{l.getGong()}方{l.getXiu()}{l.getZheng()}{l.getAnimal()}-{l.getXiuLuck()}",
                "彭祖干": l.getPengZuGan(),
                "彭祖支": l.getPengZuZhi(),
                "吉神方位": {
                    "喜神": f"{l.getDayPositionXi()} {l.getDayPositionXiDesc()}",
                    "阳贵": f"{l.getDayPositionYangGui()} {l.getDayPositionYangGuiDesc()}",
                    "阴贵": f"{l.getDayPositionYinGui()} {l.getDayPositionYinGuiDesc()}",
                    "福神": f"{l.getDayPositionFu()} {l.getDayPositionFuDesc()}",
                    "财神": f"{l.getDayPositionCai()} {l.getDayPositionCaiDesc()}"
                },    
                "太岁": f"{l.getDayPositionTaiSui(2)} {l.getDayPositionTaiSuiDesc(2)}",
                "胎神": l.getDayPositionTai(),
                "冲煞": f"{l.getDayShengXiao()}日 冲{l.getDayChongDesc()} 煞{l.getDaySha()}",
                # "纳音": {"年": l.getYearNaYin(), "月": l.getMonthNaYin(), "日": l.getDayNaYin()},
                "八字": l.getEightChar().toString(),
                "建除日": f"{l.getDayNaYin()} {l.getZhiXing()}执位",
                "十二天神": f"{l.getDayTianShen()}({l.getDayTianShenType()}) {l.getDayTianShenLuck()}",
                "宜": ". ".join(l.getDayYi()),
                "忌": ". ".join(l.getDayJi()),
                "吉神": ". ".join(l.getDayJiShen()),
                "凶煞": ". ".join(l.getDayXiongSha()),
                "月相": f"{l.getYueXiang()}月",
                "季节": l.getSeason(),
                "九星": l.getDayNineStar().toFullString()
            }
        }
