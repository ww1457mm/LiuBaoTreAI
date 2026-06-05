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
        request({
          url: '/api/user/login',
          method: 'POST',
          data: { code: res.code || 'guest' }
        }).then((data) => {
          this.globalData.openid = data.openid
          wx.setStorageSync('openid', data.openid)
          this.globalData.userInfo = data
          wx.setStorageSync('userInfo', data)
        }).catch(() => {
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
