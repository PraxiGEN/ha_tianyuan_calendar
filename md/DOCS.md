# 使用指南 (Documentation)

---

## ⚙️ 配置 (Configuration)

### 步骤 1：添加集成
1. 进入 Home Assistant 的 **设置 -> 设备与服务 -> 添加集成**。
2. 搜索并选择 **天元农历 (TianYuan Lunar)**。
3. 在配置界面填写以下基础信息：
   - **自定义经度**：输入您所在位置的经度（例如：北京 116.4、上海 121.4）。用于计算极其精确的**真太阳时**，默认为自动识别`HA地点`。
   - **刷新频率**：建议设置为 `1` 至 `5` 分钟，以保证时辰和真太阳时状态实时更新。

### 步骤 2：选项设置 (UI Options)
集成添加后，点击 **“选项”** 可实时调整以下高级参数：

- **计算模式 (Calculation Mode)**：
  - `系统时间 (ST)`：默认模式。农历属性（宜忌、干支等）参考北京时间。
  - `真太阳时 (TST)`：专业模式。农历属性完全依据地理位置的真实太阳高度角计算。

- **开启更多实体**：开启后农历设备生成更多实体。
- **开启天元岐黄**：开启后将添加子设备（TianYuan QiHuang）生成子午流注（纳甲、纳子）、灵龟八法，五运六气等专业医学传感器。
- **开启天元术数**：开启后将添加子设备（TianYuan ShuShu）生成小六壬，梅花易数，皇极经世，易经卦象等术数传感器。

- **配置/修改家人生日清单**: 开启后将进入生日管理二级界面，支持自定义输入生日信息，支持多人。
  - 支持格式：姓名 出生日期 [农历]
  - 例如：张三1994-04-26      （默认添加为公历）
  - 例如：李四 1995-05-20 农历
  - 说明：生日提醒支持农历转公历，公历转农历，所以默认添加两个生日信息。


---

## 🌓 核心逻辑：两个“宇宙”

为了兼顾日常生活与专业推算，集成内部运行着两套逻辑：

| 模式 | 逻辑基础 | 适用场景 |
| :--- | :--- | :--- |
| **ST (System Time)** | 墙上挂钟的时间 (UTC+8) | 查看法定节假日、日常农历日期、看表过日子。 |
| **TST (True Solar Time)** | 经度修正 + 均时差修正 | 八字排盘、中医针灸取穴、精准时辰判定。 |

---

## 🛠️ 传感器列表 (Entities)

### 1. 核心历法（默认添加）
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_nong_li_lunar_calendar` | **农历** | **状态**：显示当前农历。**属性**：包含所有农历信息。 |
| `sensor.tianyuan_nong_li_holiday` | **假期信息** | **状态**：工作日/节假日。**属性**：当日节日、未来 10 个节假日深度预报。 |
| `sensor.tianyuan_nong_li_solar_term` | **节气信息** | **状态**：今日节气或下个节气倒计时。**属性**：前后节气日期及精确时刻。 |
| `sensor.tianyuan_nong_li_shi_er_shi_chen` | **十二时辰** | **状态**：钟表时辰。**属性**：全天 12 时辰宜忌全表、干支及吉凶预报。 |
| `calendar.tianyuan_nong_li_birthday_reminder` | **生日提醒** | **状态**：达成条件显示生日信息。**属性**：生日信息。 |
| `calendar.tianyuan_nong_li_tianyuan_calendar` | **天元历法** | **状态**：始终显示单日农历信息。**属性**：农历信息。 |

### 2. 八字，冲煞等更多历法相关（需开启更多实体）
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_nong_li_four_pillars_of_destiny` | **四柱八字** | **状态**：显示乾造/坤造及四柱。**属性**：五行、纳音、十神、长生十二神(地势)、胎元、命宫、身宫。 |
| `sensor.tianyuan_nong_li_chong_sha` | **冲煞** | **状态**：显示冲煞。**属性**：当日生肖、相冲、相刑、相害、相破、三合、六合。 |
| `sensor.tianyuan_nong_li_true_solar_time` | **真太阳时** | **状态**：当前地点的时辰。**属性**：实时真太阳时、时柱宜忌、神位、冲煞。 |
| `sensor.tianyuan_nong_li_heavenly_stems_earthly_branches` | **天干地支** | **状态**：年月日精准干支。**属性**：分项展示年/月/日的干支详情及其纳音五行。 |
| `sensor.tianyuan_nong_li_shi_er_tian_shen` | **十二天神** | **状态**：黄黑道判定。**属性**：包含“道远几时通达”等传统择日口诀。 |
| `sensor.tianyuan_nong_li_dong_fang_xing_xiu` | **东方星宿** | **状态**：所属星宿、方位及吉凶（如：东方角木蛟-吉）。 |

### 3. 天元岐黄 (需开启天元岐黄)
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_lunar_najia` | **子午流注-纳甲** | 实时显示开穴经络、穴位、经络五行及天干。 |
| `sensor.tianyuan_lunar_nazi` | **子午流注-纳子** | 实时展示当前时辰对应的循行经络。 |
| `sensor.tianyuan_lunar_linggui` | **灵龟八法** | 依据真太阳时与性别计算的实时八法开穴数据。 |
| `sensor.tianyuan_qi_huang_fei_teng_ba_fa` | **飞腾八法** | 依据真太阳时的实时八法开穴数据。 |
| `sensor.tianyuan_qi_huang_ying_sui_bu_xie` | **迎随补泻** | 实时展示当前时辰对应的循行经络。 |
| `sensor.tianyuan_qi_huang_liu_bu_qi_ji` | **六步气机** | 依据真太阳时的实时五运六气数据。 |
| `sensor.tianyuan_qi_huang_nian_du_wu_yun_liu_qi_zong_lan` | **年度五运六气总览** | 依据真太阳时的实时五运六气数据。 |

### 4. 天元术数 (需开启天元术数)
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_shushu_xiaoliuren` | **小六壬时卦** | 依据月日时计算的时卦数据。 |
| `sensor.tianyuan_shushu_hourly_hexagram` | **梅花易数时卦** | 依据年月日时计算的时卦数据。 |
| `sensor.tianyuan_shushu_monthly_hexagram` | **皇极经世值月卦** | 依据年月计算的皇极经世数据。 |
| `sensor.tianyuan_shushu_i_ching` | **易经卦象** | 实时展示基于梅花易数计算结果的卦的完整卦辞。 |

---

## 📈 前端展示建议

### 示例 1：Lunar Info Card
```yaml
type: custom:tianyuan-lunar-card
entity: sensor.tianyuan_nong_li_lunar_calendar  #默认
```

### 示例 1：Lunar Info Card
```yaml
type: custom:lunar-info-card
entity: sensor.tianyuan_nong_li_lunar_calendar  #默认
```

## 💡 常见问题 (FAQ)

#### Q: 为什么我的真太阳时和北京时间差了很久？
#### A: 这是正常的。北京时间以东经 120 度为准，如果你在成都（约 104 度），真太阳时会比北京时间晚约 1 小时。本集成通过您配置的经度及地球公转偏差（均时差）进行了精确修正。

#### Q: 为什么其他农历显示的天干地支和集成中的不一样？
#### A: 本集成严格遵循术数传统，新年以立春节气交接的时刻，晚子时日柱算当天，为准确划分点。 （该划分点不再讨论）

#### Q: 八字计算的年柱是以什么为界？
#### A: 本集成严格遵循术数传统，年柱与月柱均以**二十四节气（立春、惊蛰等）**的交接时刻为准确划分点，而非正月初一。
