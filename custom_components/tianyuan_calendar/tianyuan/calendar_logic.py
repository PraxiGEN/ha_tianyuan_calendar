"""天元历法引擎 - 日历事件与生日逻辑处理."""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any
from homeassistant.components.calendar import CalendarEvent
from lunar_python import Lunar, Solar

class 天元日历逻辑类:
    """负责日历事件的解析、匹配与包装"""

    @staticmethod
    def 包装多行历书事件法(当前日期: date, 日数据: dict) -> list[CalendarEvent]:
        """将单日数据拆分为多行日历事件，每行带独立描述"""
        结果 = []
        属性 = 日数据.get("全量属性数据", {})
        假期包 = 日数据.get("假期数据", {})
        节气包 = 日数据.get("节气数据", {})
        # 深入一层
        假期 = 假期包.get("attributes", {})
        节气 = 节气包.get("attributes", {})
        

        农历描述 = (
            f"【历法】农历 {属性.get('农历')} · {属性.get('星期')}\n"
            f"【物候】{属性.get('物候')}\n"
            f"【月相】{属性.get('月相')}\n"
            f"【季节】{属性.get('季节')}\n"
            f"【九星】{属性.get('九星')}"
        )
        结果.append(CalendarEvent(
            start=当前日期,
            end=当前日期 + timedelta(days=1),
            summary=属性.get("农历", ""),
            description=农历描述,
            location="农历日期"
        ))

        标题项 = []
        节气名 = 节气包.get("节气名", "") 
        if 节气名: 标题项.append(节气名)
        显示列表 = 假期包.get("显示列表", [])

        if 显示列表:
            标题项.extend(显示列表)

        if 标题项:
 
            假期信息 = 假期 .get("假期信息", {})
            是否工作日 = 假期信息.get("是否工作日", "是")
            法定名 = 假期信息.get("名称", "无假期")

            # 确定性质文案（更高级的显示）
            if 法定名 != "无假期":
                性质文字 = "法定节假日" if 是否工作日 == "否" else "调休工作日 (补班)"
            else:
                性质文字 = "普通工作日" if 是否工作日 == "是" else "周末休息"

            节气描述 = (
                f"【时令】{节气.get('上一节气')} ➔ {节气.get('下一节气')}\n"
                f"【节日】{' / '.join(标题项)}\n"
                f"【性质】{性质文字}"
            )
            结果.append(CalendarEvent(
                start=当前日期,
                end=当前日期 + timedelta(days=1),
                summary=" | ".join(filter(None, 标题项)),
                description=节气描述,
                location="节日节气"
            ))

        干支全文 = 属性.get('天干地支', '')
        部分 = 干支全文.split(' ')
        if len(部分) >= 3:
            # 年干支
            结果.append(CalendarEvent(
                start=当前日期,
                end=当前日期 + timedelta(days=1),
                summary=部分[0],
                description=f"【岁次】{部分[0]}\n【日禄】{属性.get('日禄')}\n【太岁】{属性.get('太岁')}\n【胎神】{属性.get('胎神')}",
                location="年干支"
            ))
            # 月日干支
            结果.append(CalendarEvent(
                start=当前日期,
                end=当前日期 + timedelta(days=1),
                summary=f"{部分[1]} {部分[2]}",
                description=(
                    f"【月日】{部分[1]} {部分[2]}\n"
                    f"【建除】{属性.get('建除日')}\n"
                    f"【宜】{属性.get('宜')}\n"
                    f"【忌】{属性.get('忌')}\n"
                    f"【冲煞】{属性.get('冲煞')}\n"
                    f"【彭祖】{属性.get('彭祖干')} / {属性.get('彭祖支')}\n"
                    f"【神煞】吉神: {属性.get('吉神')} | 凶煞: {属性.get('凶煞')}"
                ),
                location="月日干支"
            ))
        return 结果

    @staticmethod
    def 检测并包装生日事件集类(目标日期: date, 农历对象: Lunar, 阳历对象: Solar, 生日配置: list[str]) -> list[CalendarEvent]:
        """
        支持双重生日自动转换与匹配。
        输入格式支持：'张三 1992-10-25 农历' 或 '李四1995-05-20'
        """
        if not 生日配置 or not 农历对象 or not 阳历对象:
            return []
        
        匹配结果 = []
        # 当前查看日期的特征
        当前阳历月日 = (阳历对象.getMonth(), 阳历对象.getDay())
        当前农历月日 = (农历对象.getMonth(), 农历对象.getDay())

        for 项 in 生日配置:
            # 匹配模式：(姓名) (YYYY-MM-DD格式日期) (可选的农历后缀)
            match = re.match(r"^([^\d\s-]+)\s*(\d{4}-\d{1,2}-\d{1,2})\s*(农历|农)?$", 项.strip())
            if not match:
                continue

            try:
                姓名 = match.group(1)
                出生日期串 = match.group(2)
                后缀 = match.group(3)
                
                # 拆分年月日
                y, m, d = map(int, 出生日期串.split("-"))
                # 自动互转逻辑
                if 后缀 and "农" in 后缀:
                    # 输入是农历
                    出生农历 = Lunar.fromYmd(y, m, d)
                    出生阳历 = 出生农历.getSolar()
                else:
                    # 输入是公历
                    出生阳历 = Solar.fromYmd(y, m, d)
                    出生农历 = 出生阳历.getLunar()

                农历生日月日 = (出生农历.getMonth(), 出生农历.getDay())
                公历生日月日 = (出生阳历.getMonth(), 出生阳历.getDay())
                # 判定农历生日是否是今天
                if 当前农历月日 == 农历生日月日:
                    匹配结果.append(CalendarEvent(
                        start=目标日期,
                        end=目标日期 + timedelta(days=1),
                        summary=f"🎂 {姓名} 的农历生日",
                        description=f"【农历生日】{出生农历.toString()}\n【对应公历】{出生阳历.toYmd()}\n祝：生日快乐，万事如意！",
                        location="天元历书·生日提醒"
                    ))
                # 判定公历生日是否是今天
                if 当前阳历月日 == 公历生日月日:
                    匹配结果.append(CalendarEvent(
                        start=目标日期,
                        end=目标日期 + timedelta(days=1),
                        summary=f"🎂 {姓名} 的公历生日",
                        description=f"【公历生日】{出生阳历.toYmd()}\n【对应农历】{出生农历.toString()}\n祝：生日快乐，岁岁平安！",
                        location="天元历书·生日提醒"
                    ))

            except Exception:
                continue
                
        return 匹配结果

    @staticmethod
    def 包装单日生日摘要类(目标日期: date, 农历对象: Lunar, 阳历对象: Solar, 生日配置: list[str]) -> dict | None:
        """
        为 calendar.py 的 event 属性提供今日生日摘要 (用于状态栏).
        """
        # 调用检测方法获取今天的生日事件列表
        事件集 = 天元日历逻辑类.检测并包装生日事件集类(目标日期, 农历对象, 阳历对象, 生日配置)
        
        if not 事件集:
            return None

        # 合并所有人的姓名和描述
        所有摘要 = [e.summary for e in 事件集]
        所有描述 = [e.description for e in 事件集]

        return {
            "start": 目标日期,
            "end": 目标日期 + timedelta(days=1),
            "summary": " | ".join(所有摘要),
            "description": "\n".join(所有描述),
            "location": "家人生日"
        }

    @staticmethod
    def 包装单日摘要事件法(单日数据: dict, 目标日期: date) -> dict | None:
        """为 calendar.py 的 event 属性提供今日摘要包装 (单行)"""
        属性 = 单日数据.get("全量属性数据", {})
        if not 属性: return None
        
        描述 = (
            f"农历 {属性.get('农历')} · {属性.get('星期')}\n"
            f"〖干支〗{属性.get('天干地支')}\n"
            f"〖建除〗{属性.get('建除日')}\n"
            f"〖神煞〗吉神: {属性.get('吉神')} / 凶煞: {属性.get('凶煞')}\n"
            f"〖彭祖〗{属性.get('彭祖干')} {属性.get('彭祖支')}\n"
            f"〖宜〗{属性.get('宜')}\n"
            f"〖忌〗{属性.get('忌')}\n"
        )
        return {
            "start": 目标日期,
            "end": 目标日期 + timedelta(days=1),
            "summary": 属性.get("农历", ""),
            "description": 描述,
            "location": 属性.get("东方星宿")
        }