Page({
  data: {
    teas: [
      { id: 'liubao', name: '六堡茶', icon: '🍵', temp: '100°C', ratio: '1:20', firstTime: 15, increment: 5, desc: '沸水冲泡，出汤要快' },
      { id: 'shengpu', name: '生普洱', icon: '🌿', temp: '95°C', ratio: '1:15', firstTime: 10, increment: 5, desc: '高温快出，保留鲜爽' },
      { id: 'shupu', name: '熟普洱', icon: '🍂', temp: '100°C', ratio: '1:20', firstTime: 15, increment: 5, desc: '沸水闷泡，汤感醇厚' },
      { id: 'black', name: '红茶', icon: '🫖', temp: '90°C', ratio: '1:50', firstTime: 30, increment: 10, desc: '水温不宜过高，避免苦涩' },
      { id: 'green', name: '绿茶', icon: '🌱', temp: '80°C', ratio: '1:50', firstTime: 45, increment: 15, desc: '低温冲泡，保留鲜味' },
      { id: 'white', name: '白茶', icon: '🤍', temp: '90°C', ratio: '1:30', firstTime: 20, increment: 10, desc: '可煮可泡，越陈越香' }
    ],
    selected: null,
    brewing: false,
    paused: false,
    steepCount: 0,
    totalTime: 0,
    remainTime: 0,
    progress: 100,
    displayTime: '00',
    timer: null,
    endTimestamp: 0,
    pauseRemain: 0
  },

  onReady() {
    this.drawProgress()
  },

  onUnload() {
    this.clearTimer()
  },

  selectTea(e) {
    const id = e.currentTarget.dataset.id
    const tea = this.data.teas.find(t => t.id === id)
    if (tea) {
      this.clearTimer()
      this.setData({
        selected: tea,
        brewing: false,
        paused: false,
        steepCount: 0,
        totalTime: 0,
        remainTime: 0,
        progress: 100,
        displayTime: '00'
      }, () => this.drawProgress())
    }
  },

  startBrew() {
    const { selected, steepCount } = this.data
    if (!selected) return

    const time = selected.firstTime + selected.increment * steepCount
    const now = Date.now()
    this.setData({
      brewing: true,
      paused: false,
      steepCount: steepCount + 1,
      totalTime: time,
      remainTime: time,
      endTimestamp: now + time * 1000,
      progress: 100,
      displayTime: this._padTime(time)
    }, () => this.drawProgress())
    this.startTimer()
  },

  _padTime(t) {
    t = Math.max(0, Math.round(t))
    return t < 10 ? '0' + t : String(t)
  },

  startTimer() {
    this.clearTimer()
    const tick = () => {
      const { endTimestamp, totalTime } = this.data
      const now = Date.now()
      const remain = Math.max(0, Math.round((endTimestamp - now) / 1000))

      if (remain <= 0) {
        this.clearTimer()
        this.setData({
          remainTime: 0,
          progress: 0,
          displayTime: '00',
          brewing: false,
          paused: false
        }, () => this.drawProgress())
        wx.vibrateShort({ type: 'heavy' })
        setTimeout(() => wx.vibrateShort({ type: 'heavy' }), 300)
        setTimeout(() => wx.vibrateShort({ type: 'heavy' }), 600)
        wx.showToast({ title: '出汤！', icon: 'success', duration: 2000 })
        return
      }

      const progress = totalTime > 0 ? (remain / totalTime) * 100 : 0
      this.setData({
        remainTime: remain,
        progress: progress,
        displayTime: this._padTime(remain)
      })
      this.drawProgress()
    }

    tick()
    this.data.timer = setInterval(tick, 200)
  },

  togglePause() {
    if (this.data.paused) {
      const now = Date.now()
      this.setData({
        paused: false,
        endTimestamp: now + this.data.pauseRemain * 1000
      })
      this.startTimer()
    } else {
      this.clearTimer()
      this.setData({
        paused: true,
        pauseRemain: this.data.remainTime
      })
      this.drawProgress()
    }
  },

  resetTimer() {
    this.clearTimer()
    var prevCount = Math.max(0, this.data.steepCount - 1)
    this.setData({
      brewing: false,
      paused: false,
      steepCount: prevCount,
      remainTime: 0,
      progress: 100,
      displayTime: '00'
    }, () => this.drawProgress())
  },

  restartAll() {
    this.clearTimer()
    this.setData({
      brewing: false,
      paused: false,
      steepCount: 0,
      totalTime: 0,
      remainTime: 0,
      progress: 100,
      displayTime: '00'
    }, () => this.drawProgress())
  },

  clearTimer() {
    if (this.data.timer) {
      clearInterval(this.data.timer)
      this.data.timer = null
    }
  },

  drawProgress() {
    var ctx = wx.createCanvasContext('progressCanvas', this)
    if (!ctx) return
    var progress = this.data.progress
    var pct = progress / 100

    // Canvas 尺寸 320rpx ≈ 160px（在 2x 屏幕上）
    var size = 160
    var cx = size / 2
    var cy = size / 2
    var r = cx - 12
    var lineWidth = 10

    ctx.clearRect(0, 0, size, size)

    // 背景圆环
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, 2 * Math.PI)
    ctx.setStrokeStyle('#f0f0f0')
    ctx.setLineWidth(lineWidth)
    ctx.setLineCap('round')
    ctx.stroke()

    // 进度弧（从顶部顺时针）
    if (pct > 0.001) {
      var startAngle = -Math.PI / 2
      var endAngle = startAngle + 2 * Math.PI * pct
      ctx.beginPath()
      ctx.arc(cx, cy, r, startAngle, endAngle)
      ctx.setStrokeStyle('#2d5a27')
      ctx.setLineWidth(lineWidth)
      ctx.setLineCap('round')
      ctx.stroke()
    }

    ctx.draw()
  }
})
