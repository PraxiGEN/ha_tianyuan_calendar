# <img src="custom_components/tianyuan_lunar/brand/icon.png" width="64"> 🌙天元历法 (TianYuan Calendar)

[![Release](https://img.shields.io/github/v/release/hzonz/ha_tianyuan_calendar)](https://github.com/hzonz/ha_tianyuan_calendar/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hzonz/ha_tianyuan_calendar/blob/main/LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

## 天元历法不再仅仅是历法传感器，它是一个深度整合中国传统“天文、术数、医学”的智能引擎。通过真太阳时修正，为用户提供精确的排盘、取穴与卦象预测。

## ✨ 核心特性

### 📅 基础历法 (Foundation)
- **精准农历**：支持完整的农历日期、闰月提醒、月相信息。🌙
- **二十四节气**：提供节气倒计时、精确交节时刻及物候描述。🍂
- **法定节假日**：实时同步国家放假安排，包含加班调休提醒、最近节日预报。🏮

### 🔭 天文授时 (Accuracy)  
- **真太阳时 (TST)**：基于地理经度自动修正均时差，提供真正意义上的“地方时”，是术数推算与子午流注的灵魂。☀️

### ☯️ 术数与预测 (Advanced Shushu)
-  **全功能八字**：显示四柱干支、五行纳音、十神、长生十二神及生肖动合关系（三合/六合/冲刑害破）。🪵

- **周易卦象引擎**：
    - **梅花易数**：基于实时真太阳时起卦，提供体用分析、卦辞与象曰。
    - **皇极经世**：精准推算元、会、运、世大周期，并提供值年卦与动态值月卦。
    - **易经查阅器**：内置64 卦详注库，支持“实时随动”与“手动检索”双模式。
    - **马前课小六壬**：集成传统“诸葛马前课”，实时推算大安、留连、速喜等即时吉凶。

- **中医时间医学**
    - **子午流注**：集成纳甲法、纳子法、灵龟八法，实时提醒经络循行与开穴建议。🌿

### ⚙️ 逻辑化架构
- **双设备管理**：自动生成“天元农历”与“天元术数”独立设备。
- **动态清理**：关闭功能开关后，系统会自动清理注册表，不留“幽灵实体”。
  
## 📦 安装

### 通过HACS安装（推荐）

1. 在HACS的"集成"部分，点击右上角的三点菜单
2. 选择"自定义存储库"
3. 在存储库字段输入：`https://github.com/hzonz/ha_tianyuan_calendar`
4. 类别选择"集成"
5. 点击"添加"保存
6. 在HACS中找到"天元历法"集成并点击安装
7. 重启Home Assistant

### 手动安装

1. 下载最新的: `https://github.com/hzonz/ha_tianyuan_calendar`
2. 解压并将`custom_components/tianyuan_lunar`文件夹放入Home Assistant的`custom_components`目录
3. 重启Home Assistant

## 📖 文档导航
- [🚀 详细配置与使用教程 (DOCS.md)](md/DOCS.md)
- [📜 版本更新历史 (CHANGELOG.md)](md/CHANGELOG.md)


## 🤝 感谢

- 感谢 lunar-python 提供的强大核心算法库。
- 感谢作者 [6tail](https://github.com/6tail/lunar-javascript) 的开源贡献

## 🤝 贡献

欢迎贡献代码、报告问题或提出功能建议！

1. 提交Issues：报告问题或功能请求
2. 提交Pull Requests：贡献代码改进
3. 项目讨论：分享使用经验或建议

## 📄 许可证

本项目基于MIT许可证开源。详情请查看LICENSE文件。

## ❤️ 支持

如果这个项目对您有帮助，请给项目点个Star ⭐！

## 📜 免责声明

本集成提供的数据仅供传统文化研究与居家参考使用。涉及中医养生及择日等信息时，请结合专业建议。

---
**兼容版本**: Home Assistant 2024.5+
