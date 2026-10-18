/* Stable circular graph layout: frames change algorithm state, not node positions. */
class GraphCanvas {
  constructor(canvas) {
    this.canvas = canvas;
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
    const ctx = this.context;
    const state = this.step?.stateData;
    const width = Math.max(640, this.canvas.parentElement.clientWidth);
    const height = 540;
    const scale = window.devicePixelRatio || 1;
    this.canvas.width = Math.round(width * scale);
    this.canvas.height = Math.round(height * scale);
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.fillStyle = "#0d081a"; ctx.fillRect(0, 0, width, height);
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.font = "14px ui-monospace, monospace";
    const captionWidth = this.canvas.parentElement.clientWidth;
    ctx.fillStyle = "#c1a9dd";
    if (!state) { ctx.fillText("Submit a weighted graph to begin.", captionWidth / 2, 30, captionWidth - 24); return; }
    const shortest = Object.keys(state.distances).length > 0;
    ctx.fillText(shortest ? "Shortest paths / nonnegative weights" : `Forest weight: ${state.totalWeight} / Components: ${state.components.length}`, captionWidth / 2, 24, captionWidth - 24);
    const positions = {};
    state.nodes.forEach((node, index) => {
      const angle = -Math.PI / 2 + index * Math.PI * 2 / state.nodes.length;
      positions[node] = state.nodes.length === 1 ? {x: width / 2, y: 270} : {x: width / 2 + Math.cos(angle) * 190, y: 270 + Math.sin(angle) * 190};
    });
    const edgeOrder = state.edges.map((_, index) => index).sort((a, b) => Number(a === state.currentEdge) - Number(b === state.currentEdge));
    const labelBoxes = [];
    const labels = state.edges.map((edge, index) => {
      const from = positions[edge.source], to = positions[edge.target];
      const dx = to.x - from.x, dy = to.y - from.y;
      const length = Math.hypot(dx, dy) || 1;
      let choice;
      outer: for (const fraction of [.5, .35, .65, .25, .75]) {
        for (const offset of [0, 22, -22, 44, -44]) {
          const point = {x: from.x + dx * fraction - dy / length * offset, y: from.y + dy * fraction + dx / length * offset};
          choice = point;
          if (Object.values(positions).some(node => Math.hypot(node.x - point.x, node.y - point.y) < 58)) continue;
          if (labelBoxes.some(box => Math.abs(box.x - point.x) < 82 && Math.abs(box.y - point.y) < 24)) continue;
          break outer;
        }
      }
      labelBoxes.push(choice);
      return choice;
    });
    edgeOrder.forEach(index => {
      const edge = state.edges[index], from = positions[edge.source], to = positions[edge.target];
      const current = index === state.currentEdge;
      const selected = state.selectedEdges.includes(index);
      const rejected = state.rejectedEdges.includes(index);
      ctx.strokeStyle = current ? "#f468c3" : selected ? "#35dded" : rejected ? "#df7487" : "#503076";
      ctx.lineWidth = current || selected ? 4 : 2;
      ctx.setLineDash(rejected ? [6, 6] : []);
      ctx.beginPath(); ctx.moveTo(from.x, from.y); ctx.lineTo(to.x, to.y); ctx.stroke();
    });
    ctx.setLineDash([]);
    state.edges.forEach((edge, index) => {
      const point = labels[index];
      const label = `#${index}: ${edge.weight}`;
      ctx.font = "12px ui-monospace, monospace";
      const labelWidth = ctx.measureText(label).width + 12;
      ctx.fillStyle = "#0d081a"; ctx.fillRect(point.x - labelWidth / 2, point.y - 10, labelWidth, 20);
      ctx.fillStyle = index === state.currentEdge ? "#f468c3" : state.selectedEdges.includes(index) ? "#35dded" : "#c1a9dd";
      ctx.fillText(label, point.x, point.y);
    });
    state.nodes.forEach(node => {
      const point = positions[node];
      const current = node === state.currentNode;
      ctx.fillStyle = current ? "#f468c3" : state.visited.includes(node) ? "#35dded" : "#ae83f2";
      ctx.beginPath(); ctx.arc(point.x, point.y, 27, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#f0e6ff"; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = "#110a23"; ctx.font = "bold 13px ui-monospace, monospace";
      ctx.fillText(node, point.x, point.y, 47);
      if (shortest) {
        ctx.fillStyle = "#f0e6ff"; ctx.font = "12px ui-monospace, monospace";
        ctx.fillText(state.distances[node] === null ? "INF" : String(state.distances[node]), point.x, point.y + 43);
      }
    });
  }
}
