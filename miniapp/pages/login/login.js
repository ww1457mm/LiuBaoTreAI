const { request } = require('../../utils/request')

const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

Page({
  data: {
    defaultAvatar,
    nickname: '',
    avatar: '',
    loading: false,
    chosenAvatar: false,
    chosenNickname: false
  },

  onLoad() {
    const app = getApp()
    const cachedOpenid = wx.getStorageSync('openid')
    const cachedUserInfo = wx.getStorageSync('userInfo')
    if (cachedOpenid && cachedUserInfo && cachedUserInfo.nickname) {
      // 有完整资料：预填充，但不自动跳转，让用户确认
      app.globalData.openid = cachedOpenid
      app.globalData.userInfo = cachedUserInfo
      this.setData({
        nickname: cachedUserInfo.nickname || '',
        avatar: cachedUserInfo.avatar || '',
        chosenAvatar: !!(cachedUserInfo.avatar),
        chosenNickname: !!(cachedUserInfo.nickname)
      })
    }
    // 无缓存或资料不完整：停留在登录页，用户填写
  },

  onChooseAvatar(e) {
    this.setData({ avatar: e.detail.avatarUrl, chosenAvatar: true })
  },

  onNicknameInput(e) {
    const val = e.detail.value.trim()
    this.setData({ nickname: val, chosenNickname: val.length > 0 })
  },

  doLogin() {
    if (this.data.loading) return
    if (!this.data.chosenAvatar || !this.data.nickname) return

    this.setData({ loading: true })

    wx.login({
      success: (res) => {
        if (!res.code) {
          wx.showToast({ title: '授权失败，请重试', icon: 'none' })
          this.setData({ loading: false })
          return
        }
        request({
          url: '/api/user/login/wechat',
          method: 'POST',
          data: { code: res.code }
        }).then((data) => {
          if (data && data.openid) {
            const app = getApp()
            const userInfo = {
              ...data,
              nickname: this.data.nickname || '茶友',
              avatar: this.data.avatar || ''
            }
            app.globalData.openid = data.openid
            app.globalData.userInfo = userInfo
            wx.setStorageSync('openid', data.openid)
            wx.setStorageSync('userInfo', userInfo)

            request({
              url: '/api/user/profile',
              method: 'PUT',
              data: {
                openid: data.openid,
                nickname: this.data.nickname || '茶友',
                avatar: this.data.avatar || ''
              }
            }).catch(() => {})

            wx.showToast({ title: '登录成功', icon: 'success' })
            setTimeout(() => this.goHome(), 800)
          } else {
            wx.showToast({ title: '登录失败，请重试', icon: 'none' })
            this.setData({ loading: false })
          }
        }).catch(() => {
          wx.showToast({ title: '登录失败，请检查网络', icon: 'none' })
          this.setData({ loading: false })
        })
      },
      fail: () => {
        wx.showToast({ title: '授权失败，请重试', icon: 'none' })
        this.setData({ loading: false })
      }
    })
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' })
  }
})
