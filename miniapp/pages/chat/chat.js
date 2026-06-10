const { request } = require('../../utils/request')

Page({
  data: {
    messages: [],
    input: '',
    sending: false,
    scrollId: '',
    quickList: ['六堡茶历史', '冲泡方法', '存储收藏', '健康功效', '制作工艺']
  },

  onShow() {
    // 支持从首页快捷问题通过 globalData 传递（switchTab 不支持 query）
    const app = getApp()
    if (app.globalData._pendingQuestion) {
      const question = app.globalData._pendingQuestion
      app.globalData._pendingQuestion = null
      this.setData({ input: question })
      setTimeout(() => this.send(), 300)
    }
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  askQuick(e) {
    this.setData({ input: e.currentTarget.dataset.q })
    this.send()
  },

  send() {
    const question = (this.data.input || '').trim()
    if (!question || this.data.sending) return
    const app = getApp()
    const openid = app.globalData.openid || wx.getStorageSync('openid')
    const id = Date.now()
    const userMsg = { id, role: 'user', content: question }
    const history = this.data.messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }))
    this.setData({
      messages: [...this.data.messages, userMsg],
      input: '',
      sending: true,
      scrollId: `msg-${id}`
    })
    request({
      url: '/api/chat',
      method: 'POST',
      data: { openid, question, history }
    }).then((res) => {
      if (res.code === 0) {
        const aid = Date.now() + 1
        const botMsg = {
          id: aid,
          role: 'assistant',
          content: res.data.answer,
          references: res.data.references || [],
          recommendations: (res.data.recommendations || []).join('、')
        }
        this.setData({
          messages: [...this.data.messages, botMsg],
          scrollId: `msg-${aid}`
        })
      } else {
        wx.showToast({ title: res.message || '回答失败', icon: 'none' })
      }
    }).catch(() => {
      wx.showToast({ title: '网络错误', icon: 'none' })
    }).finally(() => this.setData({ sending: false }))
  },

  onFavoriteLast() {
    const msgs = this.data.messages
    const last = msgs[msgs.length - 1]
    if (!last || last.role !== 'assistant') return
    const app = getApp()
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid: app.globalData.openid,
        fav_type: 'qa',
        title: msgs[msgs.length - 2]?.content?.slice(0, 50) || '问答',
        content: last.content
      }
    }).then(() => wx.showToast({ title: '已收藏' }))
  }
})
