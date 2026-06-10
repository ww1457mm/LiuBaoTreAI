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
    wx.login({
      success: (res) => {
        if (!res.code) {
          this.devLogin()
          return
        }
        request({
          url: '/api/user/login/wechat',
          method: 'POST',
          data: { code: res.code }
        }).then((data) => {
          this.setUserSession(data)
        }).catch(() => {
          this.devLogin()
        })
      },
      fail: () => {
        this.devLogin()
      }
    })
  },

  devLogin() {
    const openid = 'dev_guest_' + Date.now()
    this.ensureUser(openid)
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
      })
    })
  },

  setUserSession(data) {
    if (!data || !data.openid) return
    this.globalData.openid = data.openid
    wx.setStorageSync('openid', data.openid)
    this.globalData.userInfo = data
    wx.setStorageSync('userInfo', data)
  }
})
