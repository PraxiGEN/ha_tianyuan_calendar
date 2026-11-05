# <img src="custom_components/tianyuan_calendar/brand/icon.png" width="64"> 🌙天元历法 (TianYuan Calendar)

[![Release](https://img.shields.io/github/v/release/PraxiGEN/ha_tianyuan_calendar)](https://github.com/PraxiGEN/ha_tianyuan_calendar/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/PraxiGEN/ha_tianyuan_calendar/blob/main/LICENSE)
[![Marketplace](https://img.shields.io/badge/Marketplace-Available-blue.svg)](https://www.hacs.xyz/docs/marketplace/)
![](https://komarev.com/ghpvc/?username=PraxiGEN&color=ff69b4)

## 天元历法不再仅仅是历法传感器，它是一个深度整合中国传统“天文、术数、医学”的智能引擎。通过真太阳时修正，为用户提供精确的排盘、取穴与卦象预测。

## ✨ 核心特性

### 系统使用本地数据库作为数据源，所有逻辑均在本地离线计算完成。

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
    - **六爻筮法**：通过文本实体录入爻象，输出六爻断卦结果（需开启专业功能）。

- **中医时间医学**
    - **子午流注**：集成纳甲法、纳子法、灵龟八法、飞腾八法、迎随补泻，实时提醒经络循行与开穴建议。🌿
    - **五运六气**：集成六步气机，年度总览。
    - **辅行诀与伤寒**：内置《辅行诀脏腑用药法要》与《伤寒杂病论》条文，按脏腑、症状、六经、方剂级联选择后输出对应用药与辨证建议（需开启专业功能）。

### ⚙️ 逻辑化架构
- **多设备管理**：默认添加天元农历设备，岐黄和术数子设备，可按需开启。
- **功能全部开放**：所有实体对所有安装用户开放，没有令牌或隐藏口令门控。深度功能（辅行诀、伤寒杂病论、六爻筮法）由选项中的 **「专业功能」** 开关启用，任何用户都可自行打开。
- **动态清理**：关闭功能开关后，系统会自动清理注册表，不留“幽灵实体”。
  
## 📦 安装

### 通过市场安装（推荐）

> 自 Home Assistant **2026.11** 起，HACS 已内置为系统自带的 **市场（Marketplace）**，位于 **设置 > 市场**，无需另行安装。

一键安装：

[![在 Home Assistant 市场中打开 天元历法。](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=PraxiGEN&repository=ha_tianyuan_calendar&category=integration)

**或者手动操作：**

1. 打开 Home Assistant，进入 **设置 > 市场**
2. 搜索 **“天元历法”**（或 `TianYuan`）
3. 进入详情页，点击 **安装**
4. 安装完成后会**直接进入配置向导**，填好经度与刷新频率即可使用

> 安装后**无需重启**：集成带配置向导，安装完成即加载并直接引导你完成配置。只有在更新已安装的集成后，系统才会提示重启（按提示操作即可）。

### 手动安装（离线/无市场环境）

1. 下载最新的 Release：
```yaml
https://github.com/PraxiGEN/ha_tianyuan_calendar
```
2. 解压并将 `custom_components/tianyuan_calendar` 文件夹放入 Home Assistant 的 `custom_components` 目录
3. 重启 Home Assistant
4. 前往 **设置 > 设备与服务 > 添加集成**，搜索 **天元历法** 完成配置

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

## 兼容版本: 

- **Home Assistant 2026.1+**
  
  本集成最低兼容 HA 2026.1 及以上版本。

- **为确保集成品牌图片正确显示，请选择 Home Assistant 2026.3+**
  
  为确保品牌图标能够正确显示，建议使用 HA 2026.3 或更高版本。
  从 2026.3 起，Home Assistant 引入了 custom_integrations 目录与 Brands Proxy API，自定义集成可以在自身目录中直接包含品牌图片。