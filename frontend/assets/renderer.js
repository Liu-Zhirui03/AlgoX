/* Render snapshots only; no sorting logic or playback timers live here. */
class CanvasBars {
  constructor(canvas) {
    this.canvas = canvas;
    this.showBuffer = canvas.dataset.showBuffer === "true";
    this.context = canvas.getContext("2d");
    this.step = null;
    this.animation = null;
    this.reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
    this.observer = new ResizeObserver(() => this.render(this.step));
    this.observer.observe(canvas.parentElement);
  }
  render(step, animate = false) {
    cancelAnimationFrame(this.animation);
    const previous = this.step;
    this.step = step;
    const width = Math.max(this.canvas.parentElement.clientWidth, (step?.stateData.length || 1) * 72);
    const height = this.showBuffer ? 420 : 330;
    const ratio = window.devicePixelRatio || 1;
    this.canvas.width = Math.round(width * ratio);
    this.canvas.height = Math.round(height * ratio);
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const pair = step?.highlights || [];
    const swap = animate && !this.reducedMotion.matches && step.action === "swap" && previous && pair.length === 2 &&
      previous.stateData[pair[0]] === step.stateData[pair[1]] && previous.stateData[pair[1]] === step.stateData[pair[0]];
    const started = performance.now();
    const frame = now => {
      const progress = swap ? Math.min(1, (now - started) / 220) : 1;
      this.draw(width, height, swap ? pair : [], progress);
      if (progress < 1) this.animation = requestAnimationFrame(frame);
    };
    this.animation = requestAnimationFrame(frame);
  }
  draw(width, height, movingPair, progress) {
    const ctx = this.context;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#0d081a";
    ctx.fillRect(0, 0, width, height);
    const values = this.step?.stateData;
    ctx.font = "14px ui-monospace, monospace";
    ctx.textAlign = "center";
    if (!values?.length) {
      ctx.fillStyle = "#c1a9dd";
      ctx.fillText("Submit numbers to load a visualization.", width / 2, height / 2);
      return;
    }
    const minimum = Math.min(0, ...values);
    const maximum = Math.max(0, ...values);
    const range = maximum - minimum || 1;
    const chartTop = 42;
    const bufferSpace = this.showBuffer ? 100 : 0;
    const chartHeight = height - 110 - bufferSpace;
    const baseline = chartTop + maximum / range * chartHeight;
    const slot = (width - 40) / values.length;
    const barWidth = Math.min(56, slot * .65);
    const active = this.step.activeRange || [];
    if (active.length === 2) {
      ctx.fillStyle = "#ae83f21c";
      ctx.fillRect(20 + active[0] * slot, chartTop - 8, (active[1] - active[0] + 1) * slot, chartHeight + 44);
      ctx.fillStyle = "#c1a9dd";
      const pivot = this.step.pivotIndex;
      const pivotLabel = Number.isInteger(pivot) ? ` / Pivot ${values[pivot]} at [${pivot}]` : "";
      ctx.fillText(`Active range [${active[0]}..${active[1]}]${pivotLabel}`, width / 2, 20, width - 40);
    }
    ctx.strokeStyle = "#725694";
    ctx.beginPath(); ctx.moveTo(16, baseline); ctx.lineTo(width - 16, baseline); ctx.stroke();
    values.forEach((value, index) => {
      let visualIndex = index;
      if (movingPair.includes(index)) {
        const other = movingPair.find(item => item !== index);
        const eased = progress * progress * (3 - 2 * progress);
        visualIndex = other + (index - other) * eased;
      }
      const x = 20 + slot * (visualIndex + .5);
      const barHeight = Math.max(4, Math.abs(value) / range * chartHeight);
      const y = value >= 0 ? baseline - barHeight : baseline;
      const highlighted = this.step.highlights.includes(index);
      ctx.fillStyle = highlighted ? (["swap", "merge", "take"].includes(this.step.action) ? "#f1ca73" : "#f468c3") :
        (this.step.sortedIndices.includes(index) ? "#35dded" : "#ae83f2");
      if (this.step.pivotIndex === index) ctx.fillStyle = "#ff9c52";
      ctx.fillRect(x - barWidth / 2, y, barWidth, barHeight);
      if (highlighted) {
        ctx.strokeStyle = "#f0e6ff";
        ctx.lineWidth = 2;
        ctx.strokeRect(x - barWidth / 2 - 3, y - 3, barWidth + 6, barHeight + 6);
        ctx.lineWidth = 1;
      }
      ctx.fillStyle = "#f0e6ff";
      const label = Math.abs(value) >= 1000000 ? value.toExponential(1) : String(value);
      ctx.fillText(label, x, value >= 0 ? y - 12 : y + barHeight + 20);
      ctx.fillStyle = "#c1a9dd";
      ctx.fillText(`[${index}]`, 20 + slot * (index + .5), height - bufferSpace - 15);
    });
    if (this.showBuffer) {
      ctx.fillStyle = "#c1a9dd";
      ctx.textAlign = "left";
      ctx.fillText("Merge buffer", 20, height - 80);
      const buffer = this.step.buffer;
      if (buffer === null || buffer === undefined) {
        ctx.fillText("No merge in progress", 20, height - 45);
      } else {
        const capacity = active.length === 2 ? active[1] - active[0] + 1 : buffer.length;
        ctx.textAlign = "center";
        for (let index = 0; index < capacity; index++) {
          const x = 20 + slot * (index + .5);
          ctx.strokeStyle = "#503076";
          ctx.strokeRect(x - barWidth / 2, height - 65, barWidth, 34);
          if (index < buffer.length) {
            ctx.fillStyle = index === buffer.length - 1 && this.step.action === "take" ? "#f1ca73" : "#35dded";
            const value = buffer[index];
            ctx.fillText(Math.abs(value) >= 1000000 ? value.toExponential(1) : String(value), x, height - 43);
          }
        }
      }
    }
  }
}
