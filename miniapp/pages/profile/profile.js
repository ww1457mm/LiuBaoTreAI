const { request } = require('../../utils/request')

const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

Page({
  data: {
    userInfo: { nickname: '茶友', avatar: '' },
    defaultAvatar,
    stats: { recognition: 0, qa: 0, favorite: 0 }
  },

  onShow() {
    const app = getApp()
    const cached = wx.getStorageSync('userInfo')
    if (cached && cached.openid) {
      this.setData({ userInfo: cached })
    } else if (app.globalData.userInfo && app.globalData.userInfo.openid) {
      this.setData({ userInfo: app.globalData.userInfo })
    } else {
      wx.showModal({
        title: '请先登录',
        content: '查看个人信息需要先登录，是否去登录？',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) wx.navigateTo({ url: '/pages/login/login' })
        }
      })
      return
    }
    this.ensureUser()
  },

  ensureUser() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return

    // 先尝试获取 profile，不存在则通过 login 创建
    request({ url: '/api/user/profile', data: { openid } })
      .then((data) => {
        this.setData({ userInfo: data })
        wx.setStorageSync('userInfo', data)
        this.loadStats()
      })
      .catch((err) => {
        // 用户不存在，调用 login 接口创建
        if (err.statusCode === 404 || (err.code && err.code !== 0)) {
          request({ url: '/api/user/login', method: 'POST', data: { openid } })
            .then((data) => {
              this.setData({ userInfo: data })
              wx.setStorageSync('userInfo', data)
              this.loadStats()
            })
            .catch(() => {})
        }
      })
  },

  loadStats() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return

    // 并行请求：历史记录 + 收藏
    Promise.all([
      request({ url: '/api/history', data: { openid, type: 'all', page: 1, page_size: 1 } }).catch(() => null),
      request({ url: '/api/favorite', data: { openid, page: 1, page_size: 1 } }).catch(() => null)
    ]).then(([historyRes, favRes]) => {
      const stats = { recognition: 0, qa: 0, favorite: 0 }

      // 解析历史记录数量
      if (historyRes && historyRes.code === 0) {
        const rec = historyRes.data && historyRes.data.recognition
        const qa = historyRes.data && historyRes.data.qa
        stats.recognition = rec && rec.total ? rec.total : 0
        stats.qa = qa && qa.total ? qa.total : 0
      }

      // 解析收藏数量
      if (favRes && favRes.code === 0) {
        stats.favorite = favRes.total || 0
      }

      this.setData({ stats })
    }).catch(() => {})
  },

  onChooseAvatar(e) {
    const avatar = e.detail.avatarUrl
    this.updateProfile({ avatar })
  },

  onNickname(e) {
    const nickname = e.detail.value
    if (nickname) this.updateProfile({ nickname })
  },

  updateProfile(partial) {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    const userInfo = { ...this.data.userInfo, ...partial }
    this.setData({ userInfo })
    request({
      url: '/api/user/profile',
      method: 'PUT',
      data: { openid, nickname: userInfo.nickname, avatar: userInfo.avatar }
    }).then(() => wx.setStorageSync('userInfo', userInfo))
      .catch((err) => {
        wx.showToast({ title: '保存失败', icon: 'none' })
      })
  },

  goHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  goKnowledge() {
    wx.navigateTo({ url: '/pages/knowledge/knowledge' })
  },

  goFavorites() {
    wx.navigateTo({ url: '/pages/favorites/favorites' })
  }
})
