const { request } = require('../../utils/request')

const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

Page({
  data: {
    userInfo: { nickname: '茶友', avatar: '' },
    defaultAvatar,
    favorites: [],
    showFav: false,
    favLoading: false,
    stats: { recognition: 0, qa: 0, favorite: 0 },
    statsLoading: false,
    recognitionStats: { total: 0, normal_count: 0, abnormal_count: 0, monthly: [] },
    barMaxCount: 1
  },

  onShow() {
    const cached = wx.getStorageSync('userInfo')
    if (cached && cached.nickname) {
      this.setData({ userInfo: cached })
    }
    this.ensureUser()
  },

  // 确保用户已注册，再加载数据
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
    this.setData({ statsLoading: true })

    // 并行请求：历史记录 + 收藏 + 识别统计
    Promise.all([
      request({ url: '/api/history', data: { openid, type: 'all', page: 1, page_size: 1 } }).catch(() => null),
      request({ url: '/api/favorite', data: { openid, page: 1, page_size: 1 } }).catch(() => null),
      request({ url: '/api/stats/recognition', data: { openid } }).catch(() => null)
    ]).then(([historyRes, favRes, statsRes]) => {
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

      // 解析识别统计
      let recognitionStats = { total: 0, normal_count: 0, abnormal_count: 0, monthly: [] }
      if (statsRes && statsRes.code === 0 && statsRes.data) {
        recognitionStats = statsRes.data
      }
      const barMaxCount = Math.max(...(recognitionStats.monthly || []).map(m => m.count), 1)

      this.setData({ stats, recognitionStats, barMaxCount, statsLoading: false })
    }).catch(() => {
      this.setData({ statsLoading: false })
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
      .catch((err) => {
        wx.showToast({ title: '保存失败', icon: 'none' })
      })
  },

  goHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  goStats() {
    wx.navigateTo({ url: '/pages/stats/stats' })
  },

  goKnowledge() {
    wx.navigateTo({ url: '/pages/knowledge/knowledge' })
  },

  goJournal() {
    wx.navigateTo({ url: '/pages/journal/journal' })
  },

  goFavorites() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return
    this.setData({ showFav: true, favLoading: true })
    request({ url: '/api/favorite', data: { openid, page: 1, page_size: 100 } })
      .then((res) => {
        if (res.code === 0) {
          this.setData({ favorites: res.data || [], favLoading: false })
        }
      })
      .catch(() => {
        this.setData({ favLoading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  closeFavorites() {
    this.setData({ showFav: false })
    this.loadStats()
  },

  removeFav(e) {
    const id = e.currentTarget.dataset.id
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')

    wx.showModal({
      title: '提示',
      content: '确定取消收藏吗？',
      success: (res) => {
        if (!res.confirm) return
        request({
          url: '/api/favorite/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          const favorites = this.data.favorites.filter((f) => f.id !== id)
          this.setData({
            favorites,
            'stats.favorite': Math.max(0, this.data.stats.favorite - 1)
          })
          wx.showToast({ title: '已取消收藏' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  }
})
