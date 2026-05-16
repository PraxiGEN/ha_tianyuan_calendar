# 🌙天元农历 (TianYuan Lunar)

[![Release](https://img.shields.io/github/v/release/hzonz/tianyuan_lunar)](https://github.com/hzonz/tianyuan_lunar/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hzonz/tianyuan_lunar/blob/main/LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

## 天元农历不仅是一个简单的农历传感器，它深度整合了中国传统术数与时间医学。通过地理经度修正，为用户提供精确到分钟的真太阳时计算，并以此为基础推导八字、子午流注等专业数据。

## ✨ 核心特性

- 🔭 天文级授时：基于地理经度自动计算真太阳时 (True Solar Time)，修正平太阳时与真实太阳高度角的偏差。☀️
- ☯️ 全功能八字：支持乾造/坤造识别，完整显示年/月/日/时四柱，及对应的五行、纳音、十神、长生十二神（地势）、胎元、命宫等。🪵
- 🩺 中医时间医学：集成子午流注（纳甲法、纳子法）、灵龟八法，为经络养生提供实时参考。🌿
- 📅 民俗择日：提供每日宜忌、十二天神、吉神凶煞、彭祖百忌、逐日太岁方位及胎神占方。✅
- 🍂 生活指南：精准的二十四节气（含倒计时）、法定节假日信息、物候、月相及东方星宿。🌙
- ⚙️ 灵活配置：支持手动切换性别、自定义经度、实时/历史日期预览模式。🔄

## 📦 安装

### 通过HACS安装（推荐）

1. 在HACS的"集成"部分，点击右上角的三点菜单
2. 选择"自定义存储库"
3. 在存储库字段输入：`https://github.com/hzonz/tianyuan_lunar`
4. 类别选择"集成"
5. 点击"添加"保存
6. 在HACS中找到"天元农历"集成并点击安装
7. 重启Home Assistant

### 手动安装

1. 下载最新的: `https://github.com/hzonz/tianyuan_lunar`
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
