/**
 * TianYuan Lunar Dashboard Card 
 */
(async () => {
  const whenDefined = (t) => customElements.whenDefined(t);
  await Promise.race([whenDefined("ha-card"), whenDefined("ha-panel-lovelace")]);

  const Lit = window.LitElement || Object.getPrototypeOf(customElements.get("ha-card"));
  const html = Lit.prototype.html;
  const css = Lit.prototype.css;

  class TianYuanLunarCard extends Lit {
    static get properties() {
      return { _hass: {}, _config: {}, _entityId: {} };
    }

    constructor() {
      super();
      this._entityId = null;
    }

    setConfig(config) {
      this._config = { ...config };
    }

    set hass(hass) {
      this._hass = hass;
      
      // --- 实体自适应逻辑 ---
      let eid = this._config.entity;
      // 1. 如果没配置或配置的实体不存在
      if (!eid || !hass.states[eid]) {
        // 2. 自动搜索匹配天元农历规则的实体 (支持你的特定 ID 或通用前缀)
        const auto = Object.keys(hass.states).find(
          (e) => e.startsWith("sensor.tianyuan_nong_li_") || e === "sensor.tianyuan_nong_li_lunar_calenda"
        );
        if (auto) {
          this._entityId = auto;
        }
      } else {
        this._entityId = eid;
      }
    }

    // 格式化宜忌标签
    _renderTags(text, color) {
      if (!text || text === "诸事不宜") return html`<span class="tag-item">${text}</span>`;
      const list = text.includes('.') ? text.split('.') : text.split(' ');
      return list.map(item => item.trim() ? html`<span class="tag-item" style="border-color:${color}22; background:${color}11">${item.trim()}</span>` : "");
    }

    render() {
      if (!this._hass || !this._entityId) {
        return html`<ha-card class="loading">正在寻找天元农历实体...</ha-card>`;
      }

      const stateObj = this._hass.states[this._entityId];
      if (!stateObj) return html`<ha-card class="error">实体不可用</ha-card>`;

      const a = stateObj.attributes;

      return html`
        <ha-card @click="${this._handleMoreInfo}">
          
          <!-- 头部：今日农历 -->
          <div class="header">
            <div class="header-left">
              <div class="lunar-main">农历${stateObj.state}</div>
              <div class="lunar-sub">${a['天干地支']} · ${a['星期']}</div>
            </div>
            <div class="header-right">
              <div class="season-tag">${a['季节']}</div>
              <div class="hou-text">${a['物候']}</div>
            </div>
          </div>

          <!-- 核心三指标 -->
          <div class="core-grid">
            <div class="core-item">
              <div class="core-label">五行建除</div>
              <div class="core-value">${a['建除日']}</div>
            </div>
            <div class="core-item">
              <div class="core-label">当日冲煞</div>
              <div class="core-value highlight">${a['冲煞']}</div>
            </div>
            <div class="core-item">
              <div class="core-label">方位星宿</div>
              <div class="core-value">${a['东方星宿']}</div>
            </div>
          </div>

          <!-- 吉神方位 -->
          <div class="god-section">
            <div class="god-item">
              <ha-icon icon="mdi:yin-yang"></ha-icon>
              <div><div class="god-label">喜神</div><div class="god-value">${a['吉神方位']?.['喜神'] || '--'}</div></div>
            </div>
            <div class="god-item">
              <ha-icon icon="mdi:cash-marker"></ha-icon>
              <div><div class="god-label">财神</div><div class="god-value">${a['吉神方位']?.['财神'] || '--'}</div></div>
            </div>
            <div class="god-item">
              <ha-icon icon="mdi:auto-fix"></ha-icon>
              <div><div class="god-label">福神</div><div class="god-value">${a['吉神方位']?.['福神'] || '--'}</div></div>
            </div>
          </div>

          <!-- 宜忌区 -->
          <div class="yiji-container">
            <div class="yiji-row">
              <div class="yiji-circle yi">宜</div>
              <div class="tag-container">${this._renderTags(a['宜'], "#4caf50")}</div>
            </div>
            <div class="yiji-row">
              <div class="yiji-circle ji">忌</div>
              <div class="tag-container">${this._renderTags(a['忌'], "#f44336")}</div>
            </div>
          </div>

          <!-- 详细神煞 -->
          <div class="detail-box">
             <div class="detail-item">
               <span class="detail-label">吉神：</span>
               <span class="detail-value text-green">${a['吉神']}</span>
             </div>
             <div class="detail-item">
               <span class="detail-label">凶煞：</span>
               <span class="detail-value text-red">${a['凶煞']}</span>
             </div>
             <div class="detail-item">
               <span class="detail-label">彭祖：</span>
               <span class="detail-value">${a['彭祖干']} ${a['彭祖支']}</span>
             </div>
          </div>

          <div class="footer">
            <span>九星：${a['九星']?.split(' ')[0]}</span>
            <span>胎神：${a['胎神']}</span>
          </div>

        </ha-card>
      `;
    }

    _handleMoreInfo() {
      const e = new CustomEvent("hass-more-info", {
        detail: { entityId: this._entityId },
        bubbles: true,
        composed: true
      });
      this.dispatchEvent(e);
    }

    static get styles() {
      return css`
        :host { display: block; }
        ha-card {
          padding: 20px;
          border-radius: var(--ha-card-border-radius, 12px);
          background: var(--card-background-color, #fff);
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
        }
        ha-card:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }

        /* Header */
        .header { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .lunar-main { font-size: 26px; font-weight: bold; color: var(--primary-color); }
        .lunar-sub { font-size: 14px; opacity: 0.7; margin-top: 2px; }
        .header-right { text-align: right; }
        .season-tag { 
          background: var(--primary-color); color: #fff; 
          padding: 2px 8px; border-radius: 4px; font-size: 11px; display: inline-block;
        }
        .hou-text { font-size: 11px; opacity: 0.5; margin-top: 5px; }

        /* Grid */
        .core-grid { 
          display: grid; grid-template-columns: 1fr 1fr 1fr; 
          gap: 10px; margin-bottom: 20px; padding: 12px;
          background: var(--secondary-background-color); border-radius: 8px;
        }
        .core-item { text-align: center; }
        .core-label { font-size: 10px; opacity: 0.6; margin-bottom: 4px; }
        .core-value { font-size: 12px; font-weight: 500; }
        .highlight { color: #f44336; }

        /* God Section */
        .god-section { display: flex; justify-content: space-between; margin-bottom: 20px; padding: 0 5px; }
        .god-item { display: flex; align-items: center; gap: 8px; }
        .god-item ha-icon { --mdc-icon-size: 20px; color: var(--primary-color); opacity: 0.7; }
        .god-label { font-size: 10px; opacity: 0.5; }
        .god-value { font-size: 13px; font-weight: 500; }

        /* YiJi Container */
        .yiji-container { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        .yiji-row { display: flex; align-items: center; gap: 12px; }
        
        /* 核心修正：宜忌圆圈居中 */
        .yiji-circle { 
          width: 28px; 
          height: 28px; 
          border-radius: 50%; 
          display: flex; 
          align-items: center; 
          justify-content: center; 
          line-height: 1; 
          color: #fff; 
          font-weight: bold; 
          font-size: 14px; 
          flex-shrink: 0;
        }
        .yi { background: #4caf50; }
        .ji { background: #f44336; }
        
        .tag-container { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag-item { 
          font-size: 12px; padding: 1px 6px; border-radius: 4px; 
          border: 1px solid transparent; white-space: nowrap; 
        }

        /* Details */
        .detail-box { 
          border-top: 1px solid var(--divider-color); 
          padding-top: 15px; display: flex; flex-direction: column; gap: 8px; 
        }
        .detail-item { font-size: 12px; display: flex; }
        .detail-label { font-weight: bold; opacity: 0.8; flex-shrink: 0; }
        .detail-value { line-height: 1.4; padding-left: 4px; }
        .text-green { color: #4caf50; }
        .text-red { color: #f44336; }

        .footer { 
          margin-top: 15px; font-size: 10px; opacity: 0.4; 
          display: flex; justify-content: space-between;
        }
        .loading { padding: 40px; text-align: center; opacity: 0.6; }
      `;
    }
  }

  // 注册卡片
if (!customElements.get("tianyuan-lunar-card")) {
  customElements.define("tianyuan-lunar-card", TianYuanLunarCard);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "tianyuan-lunar-card",
    name: "天元农历信息卡片",
    description: "自适应匹配实体的专业农历详情卡片",
    preview: true,

    getEntitySuggestion: (hass, entityId) => {

      if (
        entityId.startsWith("sensor.tianyuan_") ||
        entityId.startsWith("sensor.lunar_") ||
        entityId.includes("nongli")
      ) {
        return {
          config: {
            type: "custom:tianyuan-lunar-card",
            entity: entityId,
          },
        };
      }

      return null;
    },
  });
}
})();