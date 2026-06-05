const { request, BASE_URL } = require('../../utils/request')

Page({
  data: {
    tab: 'recognition',
    recognition: [],
    qa: []
  },

  onShow() {
    this.loadHistory()
  },

  switchTab(e) {
    this.setData({ tab: e.currentTarget.dataset.tab })
  },

  loadHistory() {
    const app = getApp()
    const openid = app.globalData.openid || wx.getStorageSync('openid')
    request({ url: '/api/history', data: { openid, type: 'all' } })
      .then((res) => {
        if (res.code === 0) {
          const recognition = (res.data.recognition || []).map((r) => ({
            ...r,
            fullUrl: r.image_url && r.image_url.startsWith('/') ? BASE_URL + r.image_url : r.image_url
          }))
          this.setData({
            recognition,
            qa: res.data.qa || []
          })
        }
      })
  },

  favQa(e) {
    const item = e.currentTarget.dataset.item
    const app = getApp()
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid: app.globalData.openid,
        fav_type: 'qa',
        target_id: item.id,
        title: item.question.slice(0, 50),
        content: item.answer
      }
    }).then(() => wx.showToast({ title: '已收藏' }))
  }
})
