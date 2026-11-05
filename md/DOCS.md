# 使用指南 (Documentation)

---

## ⚙️ 配置 (Configuration)

### 步骤 1：安装并添加集成

**从市场安装（推荐）**

1. 进入 **设置 > 市场**。
2. 搜索 **“天元历法”**（或 `TianYuan`），进入详情页。
3. 点击 **安装**。安装完成后会**直接进入配置向导**，无需重启 Home Assistant。
4. 在配置向导中填写：
   - **自定义经度**：输入您所在位置的经度（例如：北京 116.4、上海 121.4）。用于计算极其精确的**真太阳时**，默认为自动识别`HA地点`。
   - **刷新频率**：建议设置为 `1` 至 `5` 分钟，以保证时辰和真太阳时状态实时更新。
5. 提交后集成立即加载，农历、节气、十二时辰等默认实体同时生成。

**手动安装**

1. 进入 Home Assistant 的 **设置 -> 设备与服务 -> 添加集成**。
2. 搜索并选择 **天元农历 (TianYuan Lunar)**。
3. 配置同上。

### 步骤 2：选项设置 (UI Options)
集成添加后，在 **设置 > 设备与服务 > 天元历法** 卡片上点击 **“配置”**（Options），可实时调整以下高级参数。开关按界面顺序排列：

- **计算模式 (Calculation Mode)**：
  - `系统时间 (ST)`：默认模式。农历属性（宜忌、干支等）参考北京时间。
  - `真太阳时 (TST)`：专业模式。农历属性完全依据地理位置的真实太阳高度角计算。

1. **开启前端卡片资源**：加载 `www` 下的天元历法前端卡片（Lunar Card）。
2. **配置/修改生日清单**：开启后将进入生日管理二级界面，支持自定义输入生日信息，支持多人。
   - 支持格式：姓名 出生日期 [农历]
   - 例如：张三1994-04-26      （默认添加为公历）
   - 例如：李四 1995-05-20 农历
   - 说明：生日提醒支持农历转公历，公历转农历，所以默认添加两个生日信息。
3. **开启更多高级实体**：开启后农历设备生成四柱八字、冲煞、真太阳时等更多历法实体。
4. **开启天元岐黄**：开启后将添加子设备（TianYuan QiHuang）生成子午流注（纳甲、纳子）、灵龟八法，五运六气等专业医学传感器。
5. **开启天元术数**：开启后将添加子设备（TianYuan ShuShu）生成小六壬，梅花易数，皇极经世，易经卦象等术数传感器。
6. **开启专业功能**：开启后在上面的岐黄与术数设备上追加深度实体——辅行诀脏腑用药法、伤寒杂病论、六爻筮法及其级联选择器。
   - 显示条件：**天元岐黄** 与 **天元术数** 同时开启时才会出现该开关。
   - 对所有用户开放，无需令牌或任何隐藏口令；关闭该开关时，这些实体连同注册表记录一并移除。
   - ⚠️ 任一主开关（岐黄/术数）关闭时，专业功能视为关闭，其下属专业实体也会被清理。

---

## 🌓 核心逻辑：两个“宇宙”

为了兼顾日常生活与专业推算，集成内部运行着两套逻辑：

| 模式 | 逻辑基础 | 适用场景 |
| :--- | :--- | :--- |
| **ST (System Time)** | 墙上挂钟的时间 (UTC+8) | 查看法定节假日、日常农历日期、看表过日子。 |
| **TST (True Solar Time)** | 经度修正 + 均时差修正 | 八字排盘、中医针灸取穴、精准时辰判定。 |

---

## 🛠️ 实体列表 (Entities)

> 下表实体 ID 取自集成默认命名规则（`设备名 + 实体名` 经 Home Assistant 自动转写）。若你的实例曾重命名过设备、或从早期版本升级而来，历史实体 ID 会保留不随名称变化，请以 **开发者工具 → 实体** 中显示的 ID 为准。

### 1. 核心历法（默认添加）
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_nong_li_lunar_calendar` | **农历** | **状态**：显示当前农历。**属性**：包含所有农历信息。 |
| `sensor.tianyuan_nong_li_holiday` | **假期** | **状态**：工作日/节假日。**属性**：当日节日、未来 10 个节假日深度预报。 |
| `sensor.tianyuan_nong_li_solar_term` | **节气** | **状态**：今日节气或下个节气倒计时。**属性**：前后节气日期及精确时刻。 |
| `sensor.tianyuan_nong_li_shi_er_shi_chen` | **十二时辰** | **状态**：钟表时辰。**属性**：全天 12 时辰宜忌全表、干支及吉凶预报。 |
| `calendar.tianyuan_nong_li_sheng_ri_ti_xing` | **生日提醒** | **状态**：达成条件显示生日信息。**属性**：生日信息。 |
| `calendar.tianyuan_nong_li_tianyuan_calendar` | **天元历法** | **状态**：始终显示单日农历信息。**属性**：农历信息。 |
| `button.tianyuan_nong_li_return_to_today` | **回到今天** | 将基准日期重置为今天。 |
| `date.tianyuan_nong_li_base_date_switch` | **基准日期切换** | 设定一个基准日期，所有实体按该日期推算（便于查看历史/未来日期的农历）。 |

### 2. 八字、冲煞等更多历法相关（需开启更多高级实体）
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
| `sensor.tianyuan_qi_huang_na_jia_shi_fa` | **纳甲筮法** | 实时显示开穴经络、穴位、经络五行及天干。 |
| `sensor.tianyuan_qi_huang_na_zi_shi_fa` | **纳子筮法** | 实时展示当前时辰对应的循行经络。 |
| `sensor.tianyuan_qi_huang_ling_gui_ba_fa` | **灵龟八法** | 依据真太阳时与性别计算的实时八法开穴数据。 |
| `sensor.tianyuan_qi_huang_fei_teng_ba_fa` | **飞腾八法** | 依据真太阳时的实时八法开穴数据。 |
| `sensor.tianyuan_qi_huang_ying_sui_bu_xie` | **迎随补泻** | 实时展示当前时辰对应的循行经络。 |
| `sensor.tianyuan_qi_huang_liu_bu_qi_ji` | **六步气机** | 依据真太阳时的实时五运六气数据。 |
| `sensor.tianyuan_qi_huang_nian_du_wu_yun_liu_qi_zong_lan` | **年度五运六气总览** | 依据真太阳时的实时五运六气数据。 |
| `select.tianyuan_qi_huang_ziwu_flow_gender_selection` | **子午流注性别选择** | 选择性别，灵龟八法按此计算开穴。 |

### 4. 天元术数 (需开启天元术数)
| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_zhu_shu_xiao_liu_ren_shi_gua` | **小六壬时卦** | 依据月日时计算的时卦数据。 |
| `sensor.tianyuan_zhu_shu_mei_hua_yi_shu_shi_gua` | **梅花易数时卦** | 依据年月日时计算的时卦数据。 |
| `sensor.tianyuan_zhu_shu_huang_ji_jing_shi_zhi_yue_gua` | **皇极经世月卦** | 依据年月计算的皇极经世数据。 |
| `sensor.tianyuan_zhu_shu_i_ching_hexagram` | **易经卦象** | 实时展示基于梅花易数计算结果的卦的完整卦辞。 |
| `select.tianyuan_zhu_shu_i_ching_reading_selector` | **易经查阅选择** | 手动指定卦名查阅详注，或选择“实时随动”跟随当前卦象。 |

### 5. 专业功能 (需开启专业功能，且「天元岐黄」与「天元术数」同时开启)
实体归属对应子设备：辅行诀 / 伤寒相关归 **天元岐黄**，六爻相关归 **天元术数**。

| 实体 ID | 名称 | 说明 |
| :--- | :--- | :--- |
| `sensor.tianyuan_qi_huang_fuxing_jue_zang_fu_yong_yao_fa` | **辅行诀脏腑用药法** | **状态**：依所选脏腑与症状输出的用药建议。**属性**：脏腑、症状、方剂与加减。 |
| `sensor.tianyuan_qi_huang_shang_han_za_bing_lun` | **伤寒杂病论** | **状态**：依所选六经、症状、方剂输出的辨证结果。**属性**：六经、症状、方剂与条文。 |
| `sensor.tianyuan_zhu_shu_liu_yao_shi_fa_zhan_bu` | **六爻筮法** | **状态**：依录入爻象得出的断卦结果。**属性**：本卦、变卦、动爻与断语。 |
| `select.tianyuan_qi_huang_fuxing_jue_viscera_selection` | **辅行诀大类选择** | 选择脏腑大类，驱动下方症状选择。 |
| `select.tianyuan_qi_huang_symptom_selector` | **辅行诀症状选择** | 选择具体症状，驱动辅行诀结果。 |
| `select.tianyuan_qi_huang_shang_han_channel` | **伤寒六经选择** | 选择六经（太阳、阳明、少阳、太阴、少阴、厥阴）。 |
| `select.tianyuan_qi_huang_shang_han_syndrome_selection` | **伤寒症状选择** | 选择六经下的症状。 |
| `select.tianyuan_qi_huang_shang_han_formula_selection` | **伤寒方剂选择** | 选择对应方剂，驱动伤寒结果。 |
| `text.tianyuan_zhu_shu_liu_yao_zhan_bu_text_input` | **六爻筮法文本输入** | 录入爻象（阴/阳、数字或 0/1），长度 6–40，驱动六爻结果。 |

> 上述实体在「专业功能」关闭、或岐黄/术数任一主开关关闭时会被自动移除（含注册表记录），重新开启即恢复，历史记录不受影响。

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
