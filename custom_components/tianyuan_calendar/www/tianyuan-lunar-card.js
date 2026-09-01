(async () => {
  const CARD_VERSION = "v1.0.0-lit";

  console.log(
    `%cTianYuan Lunar Card ${CARD_VERSION} Fixed`,
    "color: #1976d2; font-weight: bold; background: #e3f2fd; border: 1px solid #1976d2; border-radius: 4px; padding: 2px 6px;"
  );
  const whenDefined = (t) => customElements.whenDefined(t);
  await Promise.race([whenDefined("ha-card"), whenDefined("ha-panel-lovelace")]);

  const Lit = window.LitElement || Object.getPrototypeOf(customElements.get("ha-card"));
  const { html, css } = Lit.prototype;

  class TianYuanLunarCard extends Lit {
    static get properties() { return { hass: {}, config: {} }; }

    static getGridOptions() { return { rows: "auto", columns: 12 }; }

    static getConfigElement() { return document.createElement("tianyuan-lunar-card-editor"); }

    static getStubConfig(hass) {
      const auto = Object.keys(hass.states).find(e => e.startsWith("sensor.tianyuan_nong_li_lunar_calenda"));
      return { type: "custom:tianyuan-lunar-card", entity: auto || "" };
    }

    setConfig(config) {
      if (!config) throw new Error("Invalid configuration");
      this.config = config;
    }

    _renderTags(text, color) {
      if (!text || text === "诸事不宜") return html`<span class="tag-item">${text}</span>`;
      const list = text.includes('.') ? text.split('.') : text.split(' ');
      return list.map(item => item.trim() ? html`<span class="tag-item" style="border-color:${color}22; background:${color}11">${item.trim()}</span>` : "");
    }

    render() {
      if (!this.hass || !this.config) return html``;
      const stateObj = this.hass.states[this.config.entity];

      if (!stateObj) {
        return html`
          <ha-card class="error">
            <ha-icon icon="mdi:alert-circle-outline"></ha-icon>
            <div style="margin-top:8px;">未找到农历实体</div>
            <div style="font-size:10px;opacity:0.6;">请在编辑器中选择 sensor.tianyuan_nong_li_*</div>
          </ha-card>`;
      }

      const a = stateObj.attributes;

      return html`
        <ha-card @click="${this._handleMoreInfo}">
          <div class="header">
            <div class="header-left">
              <div class="lunar-main">农历${stateObj.state}</div>
              <div class="lunar-sub">${a['天干地支'] || '--'} · ${a['星期'] || '--'}</div>
            </div>
            <div class="header-right">
              <div class="season-tag">${a['季节'] || '--'}</div>
              <div class="hou-text">${a['物候'] || '--'}</div>
            </div>
          </div>

          <div class="core-grid">
            <div class="core-item"><div class="core-label">五行建除</div><div class="core-value">${a['建除日'] || '--'}</div></div>
            <div class="core-item"><div class="core-label">当日冲煞</div><div class="core-value highlight">${a['冲煞'] || '--'}</div></div>
            <div class="core-item"><div class="core-label">方位星宿</div><div class="core-value">${a['东方星宿'] || '--'}</div></div>
          </div>

          <div class="god-section">
            ${this._renderGod("mdi:yin-yang", "喜神", a['吉神方位']?.['喜神'])}
            ${this._renderGod("mdi:cash-marker", "财神", a['吉神方位']?.['财神'])}
            ${this._renderGod("mdi:auto-fix", "福神", a['吉神方位']?.['福神'])}
          </div>

          <div class="yiji-container">
            <div class="yiji-row"><div class="yiji-circle yi">宜</div><div class="tag-container">${this._renderTags(a['宜'], "#4caf50")}</div></div>
            <div class="yiji-row"><div class="yiji-circle ji">忌</div><div class="tag-container">${this._renderTags(a['忌'], "#f44336")}</div></div>
          </div>

          <div class="detail-box">
             <div class="detail-item"><span class="detail-label">吉神：</span><span class="detail-value text-green">${a['吉神'] || '--'}</span></div>
             <div class="detail-item"><span class="detail-label">凶煞：</span><span class="detail-value text-red">${a['凶煞'] || '--'}</span></div>
             <div class="detail-item"><span class="detail-label">彭祖：</span><span class="detail-value">${a['彭祖干'] || ''} ${a['彭祖支'] || ''}</span></div>
          </div>

          <div class="footer">
            <span>九星：${a['九星']?.split(' ')[0] || '--'}</span>
            <span>胎神：${a['胎神'] || '--'}</span>
          </div>
        </ha-card>`;
    }

    _renderGod(icon, label, value) {
      return html`<div class="god-item"><ha-icon .icon=${icon}></ha-icon><div><div class="god-label">${label}</div><div class="god-value">${value || '--'}</div></div></div>`;
    }

    _handleMoreInfo() {
      this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: this.config.entity }, bubbles: true, composed: true }));
    }

    static styles = css`
      :host { display: block; }
      ha-card { padding: 20px; border-radius: 12px; background: var(--card-background-color, #fff); cursor: pointer; transition: all 0.3s ease; }
      .error { padding: 30px; text-align: center; color: var(--secondary-text-color); }
      .header { display: flex; justify-content: space-between; margin-bottom: 20px; }
      .lunar-main { font-size: 26px; font-weight: bold; color: var(--primary-color); }
      .lunar-sub { font-size: 14px; opacity: 0.7; margin-top: 2px; }
      .header-right { text-align: right; }
      .season-tag { background: var(--primary-color); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px; display: inline-block;}
      .hou-text { font-size: 11px; opacity: 0.5; margin-top: 5px; text-align: right; }
      .core-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px; padding: 12px; background: var(--secondary-background-color); border-radius: 8px; }
      .core-item { text-align: center; }
      .core-label { font-size: 10px; opacity: 0.6; margin-bottom: 4px; }
      .core-value { font-size: 12px; font-weight: 500; }
      .highlight { color: #f44336; }
      .god-section { display: flex; justify-content: space-between; margin-bottom: 20px; }
      .god-item { display: flex; align-items: center; gap: 8px; }
      .god-item ha-icon { --mdc-icon-size: 20px; color: var(--primary-color); opacity: 0.7; }
      .god-label { font-size: 10px; opacity: 0.5; }
      .god-value { font-size: 13px; font-weight: 500; }
      .yiji-container { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
      .yiji-row { display: flex; align-items: center; gap: 12px; }
      .yiji-circle { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; font-size: 14px; flex-shrink: 0; }
      .yi { background: #4caf50; }
      .ji { background: #f44336; }
      .tag-container { display: flex; flex-wrap: wrap; gap: 6px; }
      .tag-item { font-size: 12px; padding: 1px 6px; border-radius: 4px; border: 1px solid transparent; white-space: nowrap; }
      .detail-box { border-top: 1px solid var(--divider-color); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }
      .detail-item { font-size: 12px; display: flex; }
      .detail-label { font-weight: bold; opacity: 0.8; flex-shrink: 0; }
      .detail-value { line-height: 1.4; padding-left: 4px; }
      .text-green { color: #4caf50; }
      .text-red { color: #f44336; }
      .footer { margin-top: 15px; font-size: 10px; opacity: 0.4; display: flex; justify-content: space-between; }
    `;
  }

  class TianYuanLunarCardEditor extends Lit {
    static get properties() { return { hass: {}, config: {} }; }
    setConfig(c) { this.config = c; }

    set hass(h) {
      this._hass = h;
      // 瞬间锁定逻辑：仅当 entity 键不存在时执行
      if (h && this.config && !Object.prototype.hasOwnProperty.call(this.config, 'entity')) {
        const auto = Object.keys(h.states).find(e => 
          e === "sensor.tianyuan_nong_li_lunar_calenda" || e.startsWith("sensor._tianyuan_nong_li_lunar_calenda")
        );
        if (auto) this._upd({ entity: auto });
      }
    }

    _upd(v) { this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: { ...this.config, ...v } } })); }

    render() {
      if (!this.config || !this._hass) return html``;
      return html`
        <ha-form
          .hass=${this._hass}
          .data=${this.config}
          .schema=${[{ name: "entity", label: "选择天元农历实体", selector: { entity: { domain: "sensor", integration: "tianyuan_calendar" } } }]}
          .computeLabel=${s => s.label}
          @value-changed=${e => this._upd(e.detail.value)}
        ></ha-form>
      `;
    }
  }

  customElements.define("tianyuan-lunar-card", TianYuanLunarCard);
  customElements.define("tianyuan-lunar-card-editor", TianYuanLunarCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "tianyuan-lunar-card",
    name: "TianYuan Lunar Card",
    preview: false,
    description: "基于 TianYuan Calendar 的专业农历信息卡片"
  });
})();