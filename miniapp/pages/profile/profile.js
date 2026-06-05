const { request } = require('../../utils/request')

const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

Page({
  data: {
    userInfo: { nickname: '茶友', avatar: '' },
    defaultAvatar,
    favorites: [],
    showFav: false
  },

  onShow() {
    const cached = wx.getStorageSync('userInfo')
    if (cached) this.setData({ userInfo: cached })
    else this.loadProfile()
  },

  loadProfile() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return
    request({ url: '/api/user/profile', data: { openid } })
      .then((data) => {
        this.setData({ userInfo: data })
        wx.setStorageSync('userInfo', data)
      })
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
  },

  goHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  goKnowledge() {
    wx.navigateTo({ url: '/pages/knowledge/knowledge' })
  },

  goFavorites() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    this.setData({ showFav: true })
    request({ url: '/api/favorite', data: { openid } })
      .then((res) => {
        if (res.code === 0) this.setData({ favorites: res.data || [] })
      })
  },

  removeFav(e) {
    const id = e.currentTarget.dataset.id
    const openid = getApp().globalData.openid
    request({ url: `/api/favorite/${id}?openid=${openid}`, method: 'DELETE' })
      .then(() => {
        this.setData({
          favorites: this.data.favorites.filter((f) => f.id !== id)
        })
      })
  }
})
