const { request } = require('../../utils/request')

const CAT_MAP = {
  history: '历史文化',
  process: '制作工艺',
  culture: '品鉴文化',
  health: '健康功效',
  brew: '冲泡存储',
  grade: '等级品鉴',
  origin: '产地分布'
}

Page({
  data: {
    article: null,
    categoryLabel: '',
    loading: true
  },

  onLoad(options) {
    const id = options.id
    this.setData({ loading: true })
    request({ url: `/api/knowledge/${id}` })
      .then((res) => {
        if (res.code === 0) {
          this.setData({
            article: res.data,
            categoryLabel: CAT_MAP[res.data.category] || res.data.category,
            loading: false
          })
        } else {
          this.setData({ loading: false })
          wx.showToast({ title: '文章不存在', icon: 'none' })
        }
      })
      .catch(() => {
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  addFavorite() {
    const app = getApp()
    const a = this.data.article
    if (!a || !a.id) return
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid: app.globalData.openid,
        fav_type: 'knowledge',
        target_id: a.id,
        title: a.title,
        content: a.content
      }
    }).then(() => wx.showToast({ title: '收藏成功' }))
      .catch(() => wx.showToast({ title: '收藏失败', icon: 'none' }))
  }
})
