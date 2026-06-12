const { request } = require('./utils/request')

App({
  globalData: {
    userInfo: null,
    openid: ''
  },

  onLaunch() {
    this.login()
  },

  login() {
    const cached = wx.getStorageSync('openid')
    if (cached) {
      this.globalData.openid = cached
      this.ensureUser(cached)
      return
    }
    // 未登录，跳转到登录页
    if (typeof wx !== 'undefined' && wx.reLaunch) {
      wx.reLaunch({ url: '/pages/login/login' })
    }
  },

  ensureUser(openid) {
    if (!openid) return Promise.resolve()
    this.globalData.openid = openid
    wx.setStorageSync('openid', openid)
    return request({
      url: '/api/user/profile',
      data: { openid }
    }).then((data) => {
      this.setUserSession(data)
    }).catch(() => {
      return request({
        url: '/api/user/login',
        method: 'POST',
        data: { openid }
      }).then((data) => {
        this.setUserSession(data)
      }).catch(() => {})
    })
  },

  setUserSession(data) {
    if (!data || !data.openid) return
    this.globalData.openid = data.openid
    wx.setStorageSync('openid', data.openid)
    this.globalData.userInfo = data
    wx.setStorageSync('userInfo', data)
    // 通知所有页面刷新用户信息
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.onUserLoginReady) page.onUserLoginReady(data)
    })
  },

  isLoggedIn() {
    const app = getApp()
    return !!(app.globalData.userInfo || wx.getStorageSync('userInfo'))
  }
})
