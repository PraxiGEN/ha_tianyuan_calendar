"""TianYuan (天元农历) 核心协调器 """
# 干支纪日：晚子时日柱算当天
# 干支纪年：新年以立春节气交接的时刻起算
from __future__ import annotations

import math
import logging
from datetime import datetime, date, timedelta
from typing import Any, TypedDict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

# 导入外部算法库和工具类
from .tianyuan import (
    子午流注类,
    五运六气类,
    辅行诀脏腑用药法要类,
    伤寒杂病论类,
    小六壬类,
    梅花易数类,
    皇极经世类,
    六爻占卜类,
    易经详注类,
)

# 导入配置常量（保持英文，HA 依赖）
from .const import (
    DOMAIN,
    LOGGER,
    CONF_REFRESH_INTERVAL,
    CONF_CUSTOM_LONGITUDE,
    CONF_ENABLE_SHUSHU,
    CONF_ENABLE_QIHUANG,
    CONF_CALC_MODE,
    MODE_ST,
    MODE_TST,
)

# 农历库
from lunar_python import Lunar, Solar, LunarTime
from lunar_python.util import HolidayUtil

class TianYuanData(TypedDict):
    """天元协调器数据结构"""

    # ===== 基础时间数据 =====
    农历: Lunar
    阳历: Solar
    真太阳时: datetime
    实时模式: bool
    性别: str
    # ===== 农历相关数据 =====
    假期数据: dict[str, Any]
    节气数据: dict[str, Any]
    十二时辰数据: dict[str, Any]
    全量属性数据: dict[str, Any]
    更多农历实体数据: dict[str, Any]
    # ===== 岐黄（运气医学）相关数据 =====
    灵龟八法数据: dict[str, Any]
    纳甲筮法数据: dict[str, Any]
    纳子筮法数据: dict[str, Any]
    飞腾八法数据: dict[str, Any]
    迎随补泻数据: dict[str, Any]
    六步气机数据: dict[str, Any]
    年度运气总览数据: dict[str, Any]
    辅行诀结果数据: dict[str, Any]
    伤寒结果数据: dict[str, Any]
    # ===== 术数相关数据 =====
    小六壬数据: dict[str, Any]
    梅花易数数据: dict[str, Any]
    皇极经世数据: dict[str, Any]
    六爻爻法数据: dict[str, Any]
    # ===== 易经基础数据 =====
    易经名称数据: str
    易经信息数据: dict[str, Any]

class TianYuanCoordinator(DataUpdateCoordinator[TianYuanData]):
    """天元核心计算协调器"""

    def __init__(self, hass: HomeAssistant, entry, version: str) -> None:
        """初始化协调器"""

        self.entry = entry
        self.version = version

        self.查看日期: date | None = None
        self.性别: str = "男"
        self.选中卦名: str | None = None
        self.六爻输入字符串 = "阳阳阳阴阴阴"
        # --- 辅行诀联动状态 ---
        self.辅行诀选中大类 = "肝"
        self.辅行诀选中症状 = "胁下痛"
        # --- 伤寒论联动状态 ---
        self.伤寒选中六经 = "太阳"
        self.伤寒选中证型 = "太阳-表寒实"
        self.伤寒选中方名 = "麻黄汤"

        刷新间隔分钟 = entry.options.get(CONF_REFRESH_INTERVAL, 1)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=刷新间隔分钟),
        )

    # 真太阳时计算
    def _calculate_tst(self, dt: datetime, 经度: float) -> datetime:
        """计算真太阳时（True Solar Time）"""

        经度偏移分钟 = (经度 - 120) * 4
        年内序号 = dt.timetuple().tm_yday
        年内角度项 = 2 * math.pi * (年内序号 - 81) / 365
        时间方程 = 9.87 * math.sin(2 * 年内角度项) - 7.53 * math.cos(年内角度项) - 1.5 * math.sin(年内角度项)

        return dt + timedelta(minutes=经度偏移分钟 + 时间方程)

    # 主更新逻辑
    async def _async_update_data(self) -> TianYuanData:
        """异步更新数据"""
        return await self.hass.async_add_executor_job(self._获取同步数据)


    def _获取同步数据(self) -> TianYuanData:
        """同步计算主逻辑"""

        当前时间 = dt_util.now()
        实时模式 = self.查看日期 is None

        基准时间 = (
            当前时间 if 实时模式
            else datetime.combine(self.查看日期, 当前时间.time()).replace(tzinfo=当前时间.tzinfo)
        )

        # 计算真太阳时
        经度 = float(self.entry.options.get(CONF_CUSTOM_LONGITUDE, 120.0))
        真太阳时 = self._calculate_tst(基准时间, 经度)

        # 创建农历体系
        标准农历 = Lunar.fromDate(基准时间)
        真太阳时农历 = Lunar.fromDate(真太阳时)
        阳历 = Solar.fromDate(真太阳时)

        # 模式选择
        模式 = self.entry.options.get(CONF_CALC_MODE, MODE_ST)
        主农历 = 真太阳时农历 if 模式 == MODE_TST else 标准农历

        # 构建中文化数据结构
        数据: TianYuanData = {
            "农历": 主农历,
            "阳历": 阳历,
            "真太阳时": 真太阳时,
            "实时模式": 实时模式,
            "性别": self.性别,
            "假期数据": self._获取假期数据类(标准农历, 阳历, 基准时间),
            "节气数据": self._获取节气数据类(标准农历, 阳历),
            "十二时辰数据": self._获取十二时辰数据类(标准农历, 基准时间),         
            "全量属性数据": self._获取全量属性数据类(主农历, 阳历),
            "真太阳时数据": self._获取真太阳时类(真太阳时农历, 真太阳时),
            "四柱八字数据": self._获取八字类(真太阳时农历),
            "天干地支数据": self._获取干支类(真太阳时农历),
            "十二天神数据": self._获取天神类(真太阳时农历),
            "当日冲煞数据": self._获取冲煞类(真太阳时农历),
            "东方星宿数据": self._获取星宿类(真太阳时农历),            
            # 岐黄相关数据
            "纳甲筮法数据": {}, "纳子筮法数据": {}, "灵龟八法数据": {}, "飞腾八法数据": {},
            "迎随补泻数据": {}, "六步气机数据": {},
            "年度运气总览数据": {}, "辅行诀结果数据": {}, "伤寒结果数据": {},
            # 术数相关数据
            "小六壬数据": {}, "梅花易数数据": {}, "皇极经世数据": {}, "六爻爻法数据": {},
            "易经名称数据": "", "易经信息数据": {},
        }

        # 开启岐黄开关才执行
        if self.entry.options.get(CONF_ENABLE_QIHUANG):
            岐黄结果 = self._构建天元岐黄类(真太阳时农历, 真太阳时)
            数据.update(岐黄结果)


        # 开启术数开关才执行
        if self.entry.options.get(CONF_ENABLE_SHUSHU):
            术数结果 = self._构建天元术数类(真太阳时农历, 阳历)
            数据.update(术数结果)

        return 数据

    def _获取假期数据类(self, 农历, 阳历, dt):
        """假期信息"""

        假期 = HolidayUtil.getHoliday(dt.year, dt.month, dt.day)
        状态 = "工作日" if 假期 is None or 假期.isWork() else 假期.getName()

        节日列表 = []

        # 扫描前后 42 天节日
        for 偏移天数 in range(-42, 43):
            if 偏移天数 == 0:
                continue

            阳历日 = 阳历.next(偏移天数)
            农历日 = 农历.next(偏移天数)
            法定假期 = HolidayUtil.getHoliday(阳历日.getYear(), 阳历日.getMonth(), 阳历日.getDay())

            # 法定假期
            if 法定假期 and not 法定假期.isWork():
                节日列表.append({
                    "name": 法定假期.getName(),
                    "days": 偏移天数,
                    "date": 阳历日.toYmd(),
                    "type": "法定假期",
                })

            # 阳历节日
            for f in 阳历日.getFestivals():
                节日列表.append({
                    "name": f,
                    "days": 偏移天数,
                    "date": 阳历日.toYmd(),
                    "type": "阳历节日",
                })

            # 农历节日
            for f in 农历日.getFestivals():
                节日列表.append({
                    "name": f,
                    "days": 偏移天数,
                    "date": 农历日.getSolar().toYmd(),
                    "type": "农历节日",
                })

        return {
            "state": 状态,
            "当天节日": {
                "阳历节日": 阳历.getFestivals() or ["无阳历节日"],
                "农历节日": 农历.getFestivals() or ["无农历节日"],
            },
            "假期信息": {
                "名称": 假期.getName() if 假期 else "无假期",
                "类型": "法定节假日" if 假期 and not 假期.isWork() else "工作日",
                "是否工作日": "是" if (假期 is None or 假期.isWork()) else "否",
            },
            "最近节日": sorted(节日列表, key=lambda x: abs(x["days"]))[:10],
        }

    def _获取节气数据类(self, 农历, 阳历):
        """节气信息"""

        当前节气 = 农历.getCurrentJieQi()
        下一节气 = 农历.getNextJieQi()
        上一节气 = 农历.getPrevJieQi()

        下一节气日期 = datetime.strptime(下一节气.getSolar().toYmd(), "%Y-%m-%d")
        当前阳历日期 = datetime.strptime(阳历.toYmd(), "%Y-%m-%d")

        天数差 = (下一节气日期 - 当前阳历日期).days

        状态 = f"今天是{当前节气.getName()}" if 当前节气 else f"{天数差}天后是{下一节气.getName()}"

        return {
            "state": 状态,
            "上一节气": f"{上一节气.getName()} {上一节气.getSolar().toYmd()}",
            "下一节气": f"{下一节气.getName()} {下一节气.getSolar().toYmd()}",
        }

    def _获取十二时辰数据类(self, 农历, dt):
        """十二时辰"""

        当前时辰 = f"{农历.getTimeZhi()}时"
        # 13 个时辰配置
        时辰配置 = [
            ("早子时", 0), ("丑时", 1), ("寅时", 3), ("卯时", 5), ("辰时", 7),
            ("巳时", 9), ("午时", 11), ("未时", 13), ("申时", 15),
            ("酉时", 17), ("戌时", 19), ("亥时", 21), ("晚子时", 23),
        ]

        时辰结果 = {}
        for 名称, 小时 in 时辰配置:
            lt = LunarTime.fromYmdHms(农历.getYear(), 农历.getMonth(), 农历.getDay(), 小时, 0, 0)

            # 时间范围
            if 名称 == "早子时":
                时间范围 = "00:00 - 00:59"
            elif 名称 == "晚子时":
                时间范围 = "23:00 - 23:59"
            else:
                时间范围 = f"{lt.getMinHm()} - {lt.getMaxHm()}"

            时辰结果[名称] = {
                "时间": 时间范围,
                "干支": lt.getGanZhi(),
                "十二天神": f"{lt.getTianShen()}({lt.getTianShenType()}) {lt.getTianShenLuck()}",
                "吉凶": lt.getTianShenLuck(),
                "冲煞": f"冲{lt.getChongDesc()} 煞{lt.getSha()}",
                "宜": ". ".join(lt.getYi()) if lt.getYi() else "无",
                "忌": ". ".join(lt.getJi()) if lt.getJi() else "无",
            }

        return {
            "state": 当前时辰,
            "data": 时辰结果,
        }

    def _计算地支生肖的动合关系类(self, zhi: str) -> dict[str, str]:
        """计算地支生肖的动合关系（六合、三合、冲、刑、害、破）"""

        # 地支生肖关系表
        地支关系表 = {
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

        return 地支关系表.get(zhi, {
            "六合": "无", "三合": "无", "相冲": "无",
            "相刑": "无", "相害": "无", "相破": "无"
        })

    # --- 辅行诀级联动作 ---
    async def 写入辅行诀大类类(self, 大类: str):
        self.辅行诀选中大类 = 大类
        # 联动：改变大类后，症状列表会变，我们自动选该大类的第一个症状
        症状列表 = 辅行诀脏腑用药法要类.获取大类症状法(大类)
        self.辅行诀选中症状 = 症状列表[0] if 症状列表 else ""
        await self.async_refresh()

    async def 写入辅行诀症状类(self, 症状: str):
        self.辅行诀选中症状 = 症状
        await self.async_refresh()

    # --- 伤寒论级联动作 ---
    async def 写入伤寒六经类(self, 六经: str):
        """第一级触发：选经"""
        self.伤寒选中六经 = 六经
        # 立即计算该经下的证型
        证型列表 = 伤寒杂病论类.获取经下所有证型法(六经)
        if 证型列表:
            self.伤寒选中证型 = 证型列表[0]
            方名列表 = 伤寒杂病论类.获取证型下所有方名法(self.伤寒选中证型)
            if 方名列表:
                self.伤寒选中方名 = 方名列表[0]

        await self.async_refresh()

    async def 写入伤寒证型类(self, 证型: str):
        self.伤寒选中证型 = 证型

        方名列表 = 伤寒杂病论类.获取证型下所有方名法(证型)
        if 方名列表:
            self.伤寒选中方名 = 方名列表[0]
        await self.async_refresh()

    async def 写入伤寒方名类(self, 方名: str):
        # 用户也可以直接在过滤后的方名列表里选
        self.伤寒选中方名 = 方名
        await self.async_refresh()

    async def 选择实体选卦名类(self, 卦名: str):
        """由 Select 实体调用（设置选中卦名）"""
        self.选中卦名 = 卦名
        await self.async_refresh()

    # 增加供 Text 实体调用的方法
    async def 写入六爻输入类(self, value: str):
        """设置六爻输入字符串并刷新"""
        self.六爻输入字符串 = value
        await self.async_refresh()

    # --- 更多实体子逻辑 ---
    def _获取真太阳时类(self, 农历, 真太阳时):
        return {
            "state": f"{农历.getTimeZhi()}时",
            "attributes": {
                "农历": f"{农历.getMonthInChinese()}月{农历.getDayInChinese()}",
                "八字": 农历.getEightChar().toString(),
                "十二天神": f"{农历.getTimeTianShen()}({农历.getTimeTianShenType()}) {农历.getTimeTianShenLuck()}",
                "冲煞": f"冲{农历.getTimeChongDesc()} 煞{农历.getTimeSha()}",
                "宜": ". ".join(农历.getTimeYi()) if 农历.getTimeYi() else "无",
                "忌": ". ".join(农历.getTimeJi()) if 农历.getTimeJi() else "无",
                "太阳时": 真太阳时.strftime("%H:%M")
            }
        }

    def _获取八字类(self, 农历):
        八字 = 农历.getEightChar()
        性别前缀 = "乾造" if self.性别 == "男" else "坤造"
        return {
            "state": f"{性别前缀} {八字.toString()}",
            "attributes": {
                "五行": f"{八字.getYearWuXing()}, {八字.getMonthWuXing()}, {八字.getDayWuXing()}, {八字.getTimeWuXing()}",
                "纳音": f"{八字.getYearNaYin()}, {八字.getMonthNaYin()}, {八字.getDayNaYin()}, {八字.getTimeNaYin()}",
                "十神": f"{八字.getYearShiShenGan()}, {八字.getMonthShiShenGan()}, {八字.getDayShiShenGan()}, {八字.getTimeShiShenGan()}",
                "地势": f"{八字.getYearDiShi()}, {八字.getMonthDiShi()}, {八字.getDayDiShi()}, {八字.getTimeDiShi()}",
                "其他": {
                    "胎元": 八字.getTaiYuan(),
                    "命宫": 八字.getMingGong(),
                    "身宫": 八字.getShenGong()
                }
            }
        }

    def _获取干支类(self, 农历):
        return {
            "state": f"{农历.getYearInGanZhiExact()}{农历.getYearShengXiaoExact()}年 "
                     f"{农历.getMonthInGanZhiExact()}月 {农历.getDayInGanZhiExact()}日",
            "attributes": {
                "干支": {
                    "年": f"{农历.getYearInGanZhiExact()}年",
                    "月": f"{农历.getMonthInGanZhiExact()}月",
                    "日": f"{农历.getDayInGanZhiExact2()}日"
                },
                "纳音": {
                    "年": 农历.getYearNaYin(),
                    "月": 农历.getMonthNaYin(),
                    "日": 农历.getDayNaYin(),
                    "时": 农历.getTimeNaYin()
                },
                "生肖": {
                    "年": 农历.getYearShengXiaoExact(),
                    "月": 农历.getMonthShengXiaoExact(),
                    "日": 农历.getDayShengXiao(),
                    "时": 农历.getDayShengXiao()
                }
            }
        }

    def _获取天神类(self, 农历):
        return {
            "state": f"{农历.getDayTianShen()}({农历.getDayTianShenType()}) {农历.getDayTianShenLuck()}",
            "attributes": {
                "择日法": "青龙明堂与天刑，朱雀金贵天德神； 白虎玉堂天牢黑，玄武司命惊勾陈。",
                "诀曰": "道远几时通达，路遥何日还乡。"
            }
        }

    def _获取冲煞类(self, 农历):
        日支 = 农历.getDayZhiExact2()
        生肖关系 = self._计算地支生肖的动合关系类(日支)
        return {
            "state": f"{农历.getDayShengXiao()}日 冲{农历.getDayChongDesc()} 煞{农历.getDaySha()}",
            "attributes": {
                "当日生肖": 农历.getDayShengXiao(),
                "六合": 生肖关系["六合"],
                "三合": 生肖关系["三合"],
                "相冲": 生肖关系["相冲"],
                "相刑": 生肖关系["相刑"],
                "相害": 生肖关系["相害"],
                "相破": 生肖关系["相破"]
            }
        }

    def _获取星宿类(self, 农历):
        return {
            "state": f"{农历.getGong()}方{农历.getXiu()}{农历.getZheng()}{农历.getAnimal()}-{农历.getXiuLuck()}",
            "attributes": {
                "歌诀": 农历.getXiuSong()
            }
        }

    def _获取全量属性数据类(self, l: Lunar, s: Solar) -> dict[str, Any]:
        """构建全量农历属性字段"""

        return {
            "农历": f"{l.getMonthInChinese()}月{l.getDayInChinese()}",
            "星期": f"星期{l.getWeekInChinese()}",
            "天干地支": f"{l.getYearInGanZhiExact()}{l.getYearShengXiaoExact()}年 "
                       f"{l.getMonthInGanZhiExact()}月 {l.getDayInGanZhiExact2()}日",
            "日禄": l.getDayLu(),
            "物候": f"{l.getHou()} {l.getWuHou()}",
            "六曜": l.getLiuYao(),
            "七曜": l.getZheng(),
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

    def _构建天元岐黄类(self, 真太阳时农历, 真太阳时):
        """构建天元岐黄"""

        纳甲筮法 = 子午流注类.纳甲法类(真太阳时农历)
        纳子筮法 = 子午流注类.纳子法类(真太阳时)
        灵龟八法 = 子午流注类.灵龟八法类(真太阳时农历, self.性别)
        飞腾八法 = 子午流注类.飞腾八法类(真太阳时农历)
        迎随补泻 = 子午流注类.迎随补泻类(真太阳时农历, 真太阳时)
        五运六气 = 五运六气类.全量计算类(真太阳时农历)
        六步运气 = 五运六气["六步运气数据"]
        年度总览 = 五运六气["年度总览数据"]
        辅行诀结果 = 辅行诀脏腑用药法要类.辅行诀选方类(self.辅行诀选中症状)
        伤寒结果 = 伤寒杂病论类.获取方剂数据类(self.伤寒选中方名)

        return {
            "纳甲筮法数据": 纳甲筮法,
            "纳子筮法数据": 纳子筮法,
            "灵龟八法数据": 灵龟八法,
            "飞腾八法数据": 飞腾八法,
            "迎随补泻数据": 迎随补泻,
            "六步气机数据": 六步运气,
            "年度运气总览数据": 年度总览,
            "辅行诀结果数据": 辅行诀结果,
            "伤寒结果数据": 伤寒结果,
        }

    def _构建天元术数类(self, 真太阳时农历, 阳历):
        """构建天元术数"""

        小六壬 = 小六壬类.起卦(真太阳时农历)
        梅花易数 = 梅花易数类.起卦(真太阳时农历)
        皇极经世 = 皇极经世类.起卦(真太阳时农历, 阳历)
        六爻筮法 = 六爻占卜类.执行占卜流程类(self.六爻输入字符串, 真太阳时农历)

        当前时卦名 = 梅花易数.get("state")
        显示卦名 = self.选中卦名 if self.选中卦名 else 当前时卦名
        卦信息 = 易经详注类.获取详注包装类(显示卦名)

        return {
            "梅花易数数据": 梅花易数,
            "皇极经世数据": 皇极经世,
            "小六壬数据": 小六壬,
            "六爻筮法数据": 六爻筮法,
            "易经名称数据": 显示卦名,
            "易经信息数据": 卦信息,
        }

    @property
    def device_info(self):
        """定义设备模型."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="TianYuan Lunar",
            translation_key="tianyuan_lunar",
            manufacturer="TianYuan Calendar",
            sw_version=str(self.version),
            entry_type="service",
            configuration_url="https://github.com/hzonz/ha_tianyuan_calendar",
            model="察日月之度，定岁时之序。",
        )

    @property
    def qihuang_device_info(self):
        """子设备：天元岐黄."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.entry.entry_id}_qihuang")}, # 独立的设备 ID
            name="TianYuan QiHuang",
            translation_key="tianyuan_qihuang",
            manufacturer="TianYuan Calendar",
            sw_version=str(self.version),
            entry_type="service",
            via_device=(DOMAIN, self.entry.entry_id),
            model="法于阴阳，和于术数，以通天人之纪。",
        )   

    @property
    def shushu_device_info(self):
        """子设备：天元术数."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.entry.entry_id}_shushu")}, # 独立的设备 ID
            name="TianYuan ShuShu",
            translation_key="tianyuan_shushu",
            manufacturer="TianYuan Calendar",
            sw_version=str(self.version),
            entry_type="service",
            via_device=(DOMAIN, self.entry.entry_id),
            model="观天之道，执天之行，尽矣。",
        )   