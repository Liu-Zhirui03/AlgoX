/* Playback state is independent of the Canvas renderer and algorithm. */
class TracePlayer {
  constructor(onChange) {
    this.onChange = onChange;
    this.steps = [];
    this.index = 0;
    this.playing = false;
    this.speed = 1;
    this.timer = null;
  }
  emit(animate = false) { this.onChange(this.steps[this.index] || null, this, animate); }
  pause(notify = true) {
    clearTimeout(this.timer);
    this.timer = null;
    this.playing = false;
    if (notify) this.emit();
  }
  load(steps) { this.pause(false); this.steps = steps; this.index = 0; this.emit(); }
  clear() { this.load([]); }
  seek(index) {
    this.pause(false);
    this.index = Math.max(0, Math.min(index, this.steps.length - 1));
    this.emit();
  }
  next() { this.pause(false); if (this.index < this.steps.length - 1) this.index++; this.emit(true); }
  schedule() {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      if (!this.playing) return;
      this.index++;
      if (this.index >= this.steps.length - 1) this.playing = false;
      this.emit(true);
      if (this.playing) this.schedule();
    }, 1000 / this.speed);
  }
  toggle() {
    if (this.playing) { this.pause(); return; }
    if (this.steps.length < 2) return;
    if (this.index === this.steps.length - 1) this.index = 0;
    this.playing = true;
    this.emit();
    this.schedule();
  }
  setSpeed(speed) {
    this.speed = speed;
    if (this.playing) this.schedule();
  }
}
