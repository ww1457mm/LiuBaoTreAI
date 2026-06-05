const { request } = require('../../utils/request')

const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

Page({
  data: {
    userInfo: { nickname: '茶友', avatar: '' },
    defaultAvatar,
    favorites: [],
    showFav: false,
    stats: { recognition: 0, qa: 0, favorite: 0 }
  },

  onShow() {
    const cached = wx.getStorageSync('userInfo')
    if (cached) this.setData({ userInfo: cached })
    else this.loadProfile()
    this.loadStats()
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

  loadStats() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return
    Promise.all([
      request({ url: '/api/history', data: { openid, type: 'all' } }),
      request({ url: '/api/favorite', data: { openid } })
    ]).then(([historyRes, favRes]) => {
      const stats = { recognition: 0, qa: 0, favorite: 0 }
      if (historyRes.code === 0) {
        stats.recognition = (historyRes.data.recognition || []).length
        stats.qa = (historyRes.data.qa || []).length
      }
      if (favRes.code === 0) {
        stats.favorite = (favRes.data || []).length
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
        if (res.code === 0) {
          this.setData({
            favorites: res.data || [],
            'stats.favorite': (res.data || []).length
          })
        }
      })
  },

  closeFavorites() {
    this.setData({ showFav: false })
  },

  removeFav(e) {
    const id = e.currentTarget.dataset.id
    const openid = getApp().globalData.openid
    request({ url: `/api/favorite/${id}?openid=${openid}`, method: 'DELETE' })
      .then(() => {
        const favorites = this.data.favorites.filter((f) => f.id !== id)
        this.setData({
          favorites,
          'stats.favorite': favorites.length
        })
      })
  }
})
