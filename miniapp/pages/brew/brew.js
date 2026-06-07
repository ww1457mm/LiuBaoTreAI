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
    // 计时器状态
    brewing: false,
    paused: false,
    steepCount: 0,
    totalTime: 0,
    remainTime: 0,
    progress: 100,
    displayTime: '00',
    timer: null
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
      })
    }
  },

  // 开始冲泡
  startBrew() {
    const { selected, steepCount } = this.data
    if (!selected) return

    const time = selected.firstTime + selected.increment * steepCount
    this.setData({
      brewing: true,
      paused: false,
      steepCount: steepCount + 1,
      totalTime: time,
      remainTime: time,
      progress: 100,
      displayTime: String(time)
    })
    this.startTimer()
  },

  startTimer() {
    this.clearTimer()
    this.data.timer = setInterval(() => {
      let { remainTime, totalTime } = this.data
      remainTime -= 1

      if (remainTime <= 0) {
        this.clearTimer()
        this.setData({
          remainTime: 0,
          progress: 0,
          displayTime: '00',
          brewing: false,
          paused: false
        })
        // 震动提醒
        wx.vibrateShort({ type: 'heavy' })
        setTimeout(() => wx.vibrateShort({ type: 'heavy' }), 300)
        setTimeout(() => wx.vibrateShort({ type: 'heavy' }), 600)
        wx.showToast({ title: '出汤！', icon: 'success', duration: 2000 })
        return
      }

      const progress = (remainTime / totalTime) * 100
      this.setData({
        remainTime,
        progress,
        displayTime: String(remainTime)
      })
    }, 1000)
  },

  // 暂停/继续
  togglePause() {
    if (this.data.paused) {
      this.startTimer()
      this.setData({ paused: false })
    } else {
      this.clearTimer()
      this.setData({ paused: true })
    }
  },

  // 重置当前泡
  resetTimer() {
    this.clearTimer()
    this.setData({
      brewing: false,
      paused: false,
      remainTime: 0,
      progress: 100,
      displayTime: '00'
    })
  },

  // 重新开始（从第1泡）
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
    })
  },

  clearTimer() {
    if (this.data.timer) {
      clearInterval(this.data.timer)
      this.data.timer = null
    }
  },

  noop() {}
})
