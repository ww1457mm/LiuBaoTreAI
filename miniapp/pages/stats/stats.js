const { request } = require('../../utils/request')

Page({
  data: {
    stats: { total: 0, normal_count: 0, abnormal_count: 0, monthly: [], by_task: [] },
    barMaxCount: 1,
    pieNormalPct: 0,
    loading: true
  },

  onLoad() {
    this.loadStats()
  },

  onShow() {
    this.loadStats()
  },

  loadStats() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      this.setData({ loading: false })
      return
    }
    this.setData({ loading: true })
    request({ url: '/api/stats/recognition', data: { openid } })
      .then((res) => {
        if (res.code === 0) {
          const stats = res.data
          const barMaxCount = Math.max(...(stats.monthly || []).map(m => m.count), 1)
          const pieNormalPct = stats.total > 0
            ? Math.round(stats.normal_count / stats.total * 100) : 0
          this.setData({ stats, barMaxCount, pieNormalPct, loading: false })
        } else {
          this.setData({ loading: false })
        }
      })
      .catch(() => this.setData({ loading: false }))
  },

  goIdentify() {
    wx.switchTab({ url: '/pages/identify/identify' })
  }
})
