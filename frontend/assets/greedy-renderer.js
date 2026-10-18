/* Render tree forests, interval lanes, and fractional selections from snapshots. */
class GreedyCanvas {
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
    this.step = step;
    cancelAnimationFrame(this.frame);
    this.frame = requestAnimationFrame(() => this.draw());
  }
  draw() {
    const state = this.step?.stateData;
    const viewport = this.canvas.parentElement.clientWidth;
    const tree = this.mode === "huffman-tree";
    let width = Math.max(viewport, 620), height = 320;
    let positions;
    if (state && tree) {
      positions = {};
      let cursor = 0, maxDepth = 0;
      const place = (index, depth) => {
        const node = state.nodes[index];
        maxDepth = Math.max(maxDepth, depth);
        let x;
        if (node.left === null) { x = 50 + cursor * 100; cursor++; }
        else { const left = place(node.left, depth + 1), right = place(node.right, depth + 1); x = (left + right) / 2; }
        positions[index] = {x, y: 90 + depth * 86};
        return x;
      };
      for (const root of state.roots) { place(root, 0); cursor += .4; }
      width = Math.max(viewport, cursor * 100 + 40, 350);
      const coordinates = Object.values(positions).map(point => point.x);
      const minX = Math.min(...coordinates), maxX = Math.max(...coordinates);
      const offset = (width - (maxX - minX)) / 2 - minX;
      for (const point of Object.values(positions)) point.x += offset;
      height = Math.max(320, 180 + maxDepth * 86);
    } else if (state) {
      height = this.mode === "activity-timeline" ? 115 + state.activities.length * 54 : 175 + state.items.length * 53;
    }
    const ratio = window.devicePixelRatio || 1;
    this.canvas.width = Math.round(width * ratio); this.canvas.height = Math.round(height * ratio);
    this.canvas.style.width = `${width}px`; this.canvas.style.height = `${height}px`;
    const ctx = this.context;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.fillStyle = "#0d081a"; ctx.fillRect(0, 0, width, height);
    ctx.font = "14px ui-monospace, monospace"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = "#c1a9dd";
    if (!state) { ctx.fillText("Submit your input to begin.", viewport / 2, 35, viewport - 24); return; }
    if (tree) this.drawTree(ctx, state, positions, viewport);
    else if (this.mode === "activity-timeline") this.drawActivities(ctx, state, width, height, viewport);
    else this.drawKnapsack(ctx, state, width, viewport);
  }
  drawTree(ctx, state, positions, viewport) {
    ctx.fillStyle = "#c1a9dd";
    ctx.fillText(`Forest: ${state.roots.length} root(s) / Assigned bit cost: ${state.weightedCost}`, viewport / 2, 25, viewport - 24);
    for (const node of state.nodes) {
      const point = positions[node.id];
      if (!point || node.left === null) continue;
      for (const [child, bit] of [[node.left, "0"], [node.right, "1"]]) {
        const target = positions[child];
        ctx.strokeStyle = state.selected.includes(node.id) ? "#f468c3" : "#725694";
        ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(point.x, point.y); ctx.lineTo(target.x, target.y); ctx.stroke();
        const x = point.x * .5 + target.x * .5, y = point.y * .5 + target.y * .5;
        ctx.fillStyle = "#0d081a"; ctx.fillRect(x - 8, y - 9, 16, 18);
        ctx.fillStyle = "#35dded"; ctx.fillText(bit, x, y);
      }
    }
    for (const node of state.nodes) {
      const point = positions[node.id];
      if (!point) continue;
      const assigned = node.symbol !== null && Object.hasOwn(state.codes, node.symbol);
      ctx.fillStyle = state.selected.includes(node.id) ? "#f468c3" : assigned ? "#35dded" : "#ae83f2";
      ctx.beginPath(); ctx.arc(point.x, point.y, 27, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#110a23";
      ctx.font = "12px ui-monospace, monospace";
      if (node.symbol !== null) {
        ctx.fillText(node.symbol, point.x, point.y - 8, 48);
        ctx.fillText(String(node.frequency), point.x, point.y + 10, 48);
      } else ctx.fillText(String(node.frequency), point.x, point.y, 48);
      if (assigned) { ctx.fillStyle = "#35dded"; ctx.fillText(state.codes[node.symbol], point.x, point.y + 43, 94); }
    }
  }
  drawActivities(ctx, state, width, height, viewport) {
    ctx.fillStyle = "#c1a9dd";
    ctx.fillText(`Selected: ${state.selected.length} / Last finish: ${state.lastFinish ?? "none"}`, viewport / 2, 24, viewport - 24);
    const maximum = Math.max(...state.activities.map(item => item.finish), 1);
    const axis = value => 98 + value / maximum * (width - 136);
    ctx.strokeStyle = "#725694";
    ctx.beginPath(); ctx.moveTo(98, 61); ctx.lineTo(width - 38, 61); ctx.stroke();
    for (let tick = 0; tick <= 4; tick++) {
      const value = maximum * tick / 4;
      ctx.fillStyle = "#c1a9dd"; ctx.font = "12px ui-monospace, monospace";
      ctx.fillText(String(Number(value.toFixed(2))), axis(value), 47);
    }
    if (state.lastFinish !== null) {
      ctx.strokeStyle = "#35dded"; ctx.setLineDash([4, 5]);
      ctx.beginPath(); ctx.moveTo(axis(state.lastFinish), 65); ctx.lineTo(axis(state.lastFinish), height - 15); ctx.stroke(); ctx.setLineDash([]);
    }
    state.order.forEach((index, row) => {
      const item = state.activities[index], y = 87 + row * 54;
      ctx.fillStyle = "#f0e6ff"; ctx.font = "13px ui-monospace, monospace";
      ctx.fillText(item.name, 45, y + 5, 80);
      ctx.fillStyle = state.current === index ? "#f468c3" : state.selected.includes(index) ? "#35dded" : state.rejected.includes(index) ? "#df7487" : "#ae83f2";
      ctx.fillRect(axis(item.start), y - 7, Math.max(3, axis(item.finish) - axis(item.start)), 22);
      ctx.fillStyle = "#c1a9dd"; ctx.font = "12px ui-monospace, monospace";
      ctx.fillText(`[${item.start}, ${item.finish})`, (axis(item.start) + axis(item.finish)) / 2, y + 30);
    });
  }
  drawKnapsack(ctx, state, width, viewport) {
    ctx.fillStyle = "#c1a9dd";
    ctx.fillText(`Value: ${Number(state.totalValue.toFixed(4))} / Remaining: ${state.remaining}`, viewport / 2, 24, viewport - 24);
    ctx.fillStyle = "#30213e"; ctx.fillRect(20, 57, width - 40, 28);
    let offset = 20;
    state.order.forEach(index => {
      if (!state.takenWeights[index] || !state.capacity) return;
      const amount = state.takenWeights[index] / state.capacity * (width - 40);
      ctx.fillStyle = state.fractions[index] < 1 ? "#f1ca73" : "#35dded";
      ctx.fillRect(offset, 57, amount, 28);
      ctx.strokeStyle = "#0d081a"; ctx.strokeRect(offset, 57, amount, 28);
      if (amount > 35) { ctx.fillStyle = "#110a23"; ctx.fillText(state.items[index].name, offset + amount / 2, 71, amount - 8); }
      offset += amount;
    });
    ctx.fillStyle = "#c1a9dd";
    ctx.fillText(`Used weight: ${state.totalWeight} / Capacity: ${state.capacity}`, viewport / 2, 108, viewport - 24);
    state.order.forEach((index, row) => {
      const item = state.items[index], y = 157 + row * 53, fraction = state.fractions[index];
      ctx.textAlign = "left"; ctx.font = "12px ui-monospace, monospace";
      ctx.fillStyle = state.current === index ? "#f468c3" : "#f0e6ff";
      ctx.fillText(`${item.name} / w ${item.weight} / v ${item.value}`, 20, y - 7, 265);
      ctx.fillStyle = "#c1a9dd"; ctx.fillText(`ratio ${Number((item.value / item.weight).toFixed(4))}`, 20, y + 12, 265);
      const left = 300, available = width - 400;
      ctx.fillStyle = "#30213e"; ctx.fillRect(left, y - 12, available, 27);
      ctx.fillStyle = fraction < 1 ? "#f1ca73" : "#35dded"; ctx.fillRect(left, y - 12, available * fraction, 27);
      if (state.current === index) { ctx.strokeStyle = "#f468c3"; ctx.lineWidth = 2; ctx.strokeRect(left - 2, y - 14, available + 4, 31); }
      ctx.fillStyle = "#f0e6ff"; ctx.fillText(`${Number((fraction * 100).toFixed(2))}%`, width - 85, y + 1, 78);
    });
    ctx.textAlign = "center";
  }
}
