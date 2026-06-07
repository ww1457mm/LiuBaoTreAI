const { request, BASE_URL } = require('../../utils/request')

Page({
  data: {
    tab: 'recognition',
    recognition: [],
    qa: [],
    loading: true
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
    if (!openid) {
      this.setData({ loading: false })
      return
    }
    this.setData({ loading: true })
    request({ url: '/api/history', data: { openid, type: 'all', page: 1, page_size: 50 } })
      .then((res) => {
        if (res.code === 0) {
          const recData = res.data && res.data.recognition
          const qaData = res.data && res.data.qa
          const recItems = recData && recData.items ? recData.items : []
          const qaItems = qaData && qaData.items ? qaData.items : []

          const recognition = recItems.map((r) => ({
            ...r,
            fullUrl: r.image_url && r.image_url.startsWith('/') ? BASE_URL + r.image_url : r.image_url
          }))
          this.setData({ recognition, qa: qaItems, loading: false })
        } else {
          this.setData({ loading: false })
        }
      })
      .catch(() => {
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  favQa(e) {
    const item = e.currentTarget.dataset.item
    const app = getApp()
    const openid = app.globalData.openid || wx.getStorageSync('openid')
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid,
        fav_type: 'qa',
        target_id: item.id,
        title: (item.question || '').slice(0, 50),
        content: item.answer
      }
    }).then(() => {
      wx.showToast({ title: '已收藏' })
    }).catch(() => {
      wx.showToast({ title: '收藏失败', icon: 'none' })
    })
  },

  // 删除识别记录
  deleteRecord(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定删除此记录吗？',
      success: (res) => {
        if (!res.confirm) return
        const openid = getApp().globalData.openid || wx.getStorageSync('openid')
        request({
          url: '/api/history/recognition/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          const recognition = this.data.recognition.filter(r => r.id !== id)
          this.setData({ recognition })
          wx.showToast({ title: '已删除' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  },

  // 删除问答记录
  deleteQa(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定删除此记录吗？',
      success: (res) => {
        if (!res.confirm) return
        const openid = getApp().globalData.openid || wx.getStorageSync('openid')
        request({
          url: '/api/history/qa/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          const qa = this.data.qa.filter(r => r.id !== id)
          this.setData({ qa })
          wx.showToast({ title: '已删除' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  }
})
