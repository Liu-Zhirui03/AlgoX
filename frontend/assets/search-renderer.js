/* Search snapshots are rendered independently of algorithms and playback. */
class SearchCanvas {
  constructor(canvas, mode) {
    this.canvas = canvas;
    this.mode = mode;
    this.context = canvas.getContext("2d");
    this.step = null;
    this.frame = null;
    this.observer = new ResizeObserver(() => this.render(this.step));
    this.observer.observe(canvas.parentElement);
  }
  render(step) {
    cancelAnimationFrame(this.frame);
    this.step = step;
    this.frame = requestAnimationFrame(() => this.draw());
  }
  valueText(value) {
    return Math.abs(value) >= 1000000 ? value.toExponential(1) : String(value);
  }
  draw() {
    const state = this.step?.stateData;
    const hash = this.mode === "hash-search";
    const longestChain = hash && state ? Math.max(1, ...state.buckets.map(chain => chain.length)) : 1;
    const width = Math.max(this.canvas.parentElement.clientWidth, hash ? 140 + longestChain * 112 : (state?.values.length || 1) * 88 + 40);
    const height = hash && state ? 85 + state.buckets.length * 64 : 270;
    const ratio = window.devicePixelRatio || 1;
    this.canvas.width = Math.round(width * ratio);
    this.canvas.height = Math.round(height * ratio);
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    const ctx = this.context;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.fillStyle = "#0d081a";
    ctx.fillRect(0, 0, width, height);
    ctx.font = "14px ui-monospace, monospace";
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillStyle = "#c1a9dd";
    if (!state) {
      ctx.fillText("Submit numbers and a target to begin.", width / 2, height / 2, width - 40);
      return;
    }
    const captionWidth = Math.min(width, this.canvas.parentElement.clientWidth);
    if (hash) this.drawHash(ctx, state, width, captionWidth);
    else this.drawBinary(ctx, state, width, captionWidth);
  }
  drawBinary(ctx, state, width, captionWidth) {
    const slot = (width - 40) / state.values.length;
    ctx.fillStyle = "#f0e6ff";
    ctx.fillText(`Target: ${state.target}`, captionWidth / 2, 28, captionWidth - 24);
    ctx.fillStyle = "#c1a9dd";
    ctx.fillText(state.low <= state.high ? `Active bounds: low=${state.low}, high=${state.high}` : "Active range is empty", captionWidth / 2, 57, captionWidth - 24);
    state.values.forEach((value, index) => {
      const x = 20 + index * slot;
      const active = index >= state.low && index <= state.high;
      const found = state.foundIndex === index;
      const candidate = state.candidate === index;
      const middle = state.middle === index;
      ctx.fillStyle = found ? "#35dded" : middle ? "#f468c3" : candidate ? "#f1ca73" : active ? "#ae83f2" : "#30213e";
      ctx.fillRect(x + 5, 106, slot - 10, 54);
      ctx.fillStyle = found || middle || candidate || active ? "#110a23" : "#c1a9dd";
      ctx.fillText(this.valueText(value), x + slot / 2, 133, slot - 18);
      ctx.fillStyle = "#c1a9dd";
      ctx.fillText(`[${index}]`, x + slot / 2, 184);
      const labels = [];
      if (index === state.low && active) labels.push("L");
      if (index === state.high && active) labels.push("H");
      if (middle) labels.push("MID");
      if (labels.length) ctx.fillText(labels.join(" / "), x + slot / 2, 88, slot - 10);
    });
    ctx.fillStyle = "#c1a9dd";
    const note = state.foundIndex !== null ? (state.foundIndex >= 0 ? `Found at index ${state.foundIndex}` : "Target not found") :
      state.candidate !== null ? `Candidate: index ${state.candidate}; keep searching left` : "Dimmed cells are outside the active range";
    ctx.fillText(note, captionWidth / 2, 232, captionWidth - 24);
  }
  drawHash(ctx, state, width, captionWidth) {
    const active = state.bucketIndex;
    ctx.fillStyle = "#f0e6ff";
    ctx.fillText(`Target: ${state.target} / ${state.buckets.length} buckets`, captionWidth / 2, 24, captionWidth - 24);
    ctx.fillStyle = "#c1a9dd";
    const source = state.inputIndex;
    const description = source !== null ? `Insert input[${source}] = ${state.values[source]}` :
      active !== null ? `Target bucket: ${active}` : "Build the table in input order";
    ctx.fillText(description, captionWidth / 2, 49, captionWidth - 24);
    state.buckets.forEach((chain, bucket) => {
      const y = 72 + bucket * 64;
      ctx.fillStyle = active === bucket ? "#ae83f224" : "#110a23";
      ctx.fillRect(12, y, width - 24, 56);
      ctx.fillStyle = active === bucket ? "#35dded" : "#c1a9dd";
      ctx.fillText(`[${bucket}]`, 46, y + 28);
      ctx.strokeStyle = "#725694";
      ctx.beginPath(); ctx.moveTo(78, y + 28); ctx.lineTo(106, y + 28); ctx.stroke();
      if (!chain.length) {
        ctx.textAlign = "left";
        ctx.fillStyle = "#725694";
        ctx.fillText("empty", 114, y + 28);
        ctx.textAlign = "center";
      }
      chain.forEach((entry, index) => {
        const x = 108 + index * 112;
        const selected = active === bucket && state.entryIndex === index;
        const found = selected && state.foundIndex === entry.index;
        ctx.fillStyle = found ? "#35dded" : selected ? "#f468c3" : "#ae83f2";
        ctx.fillRect(x, y + 5, 94, 46);
        ctx.fillStyle = "#110a23";
        ctx.fillText(this.valueText(entry.value), x + 47, y + 19, 86);
        ctx.font = "12px ui-monospace, monospace";
        ctx.fillText(`index ${entry.index}`, x + 47, y + 38, 86);
        ctx.font = "14px ui-monospace, monospace";
        if (index + 1 < chain.length) {
          ctx.fillStyle = "#c1a9dd";
          ctx.fillText(">", x + 103, y + 28);
        }
      });
    });
  }
}
