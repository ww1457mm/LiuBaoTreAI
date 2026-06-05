const { request } = require('../../utils/request')

const CAT_MAP = { history: '历史文化', process: '制作工艺', culture: '品鉴文化', health: '健康功效' }

Page({
  data: { article: null, categoryLabel: '' },

  onLoad(options) {
    const id = options.id
    request({ url: `/api/knowledge/${id}` }).then((res) => {
      if (res.code === 0) {
        this.setData({
          article: res.data,
          categoryLabel: CAT_MAP[res.data.category] || res.data.category
        })
      }
    })
  },

  addFavorite() {
    const app = getApp()
    const a = this.data.article
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
  }
})
