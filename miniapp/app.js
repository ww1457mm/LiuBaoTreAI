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
      this.fetchProfile()
      return
    }
    wx.login({
      success: (res) => {
        if (!res.code) {
          const openid = 'dev_guest_' + Date.now()
          this.globalData.openid = openid
          wx.setStorageSync('openid', openid)
          return
        }
        // 优先使用微信真实登录接口
        request({
          url: '/api/user/login/wechat',
          method: 'POST',
          data: { code: res.code }
        }).then((data) => {
          this.globalData.openid = data.openid
          wx.setStorageSync('openid', data.openid)
          this.globalData.userInfo = data
          wx.setStorageSync('userInfo', data)
        }).catch(() => {
          // 微信登录失败，降级为开发模式
          const openid = 'dev_guest_' + Date.now()
          this.globalData.openid = openid
          wx.setStorageSync('openid', openid)
        })
      },
      fail: () => {
        const openid = 'dev_guest_' + Date.now()
        this.globalData.openid = openid
        wx.setStorageSync('openid', openid)
      }
    })
  },

  fetchProfile() {
    const openid = this.globalData.openid
    if (!openid) return
    request({
      url: '/api/user/profile',
      data: { openid }
    }).then((data) => {
      this.globalData.userInfo = data
      wx.setStorageSync('userInfo', data)
    }).catch(() => {})
  }
})
