const { request } = require('../../utils/request')

const TYPE_MAP = {
  knowledge: '知识',
  qa: '问答',
  recognition: '识别'
}

Page({
  data: {
    favorites: [],
    loading: true
  },

  onShow() {
    this.loadFavorites()
  },

  loadFavorites() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) {
      this.setData({ loading: false, favorites: [] })
      return
    }
    this.setData({ loading: true })
    request({ url: '/api/favorite', data: { openid, page: 1, page_size: 100 } })
      .then((res) => {
        if (res.code === 0) {
          const favorites = (res.data || []).map((item) => ({
            ...item,
            typeLabel: TYPE_MAP[item.fav_type] || item.fav_type
          }))
          this.setData({ favorites })
        }
      })
      .catch(() => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
      .finally(() => this.setData({ loading: false }))
  },

  removeFav(e) {
    const id = e.currentTarget.dataset.id
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')

    wx.showModal({
      title: '提示',
      content: '确定取消收藏吗？',
      success: (res) => {
        if (!res.confirm) return
        request({
          url: '/api/favorite/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          const favorites = this.data.favorites.filter((f) => f.id !== id)
          this.setData({ favorites })
          wx.showToast({ title: '已取消收藏' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  }
})
