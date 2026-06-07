const { request, BASE_URL } = require('../../utils/request')

const TEA_TYPES = {
  liubao: '六堡茶', shengpu: '生普洱', shupu: '熟普洱',
  black: '红茶', green: '绿茶', white: '白茶', oolong: '乌龙茶'
}

Page({
  data: {
    list: [],
    loading: true,
    page: 1,
    hasMore: true
  },

  onShow() {
    this.setData({ list: [], page: 1 })
    this.loadList()
  },

  loadList() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return
    this.setData({ loading: true })
    request({ url: '/api/journal', data: { openid, page: this.data.page, page_size: 20 } })
      .then((res) => {
        if (res.code === 0) {
          const items = (res.data || []).map(j => ({
            ...j,
            typeName: TEA_TYPES[j.tea_type] || j.tea_type,
            fullUrl: j.image_url && j.image_url.startsWith('/') ? BASE_URL + j.image_url : j.image_url
          }))
          this.setData({
            list: this.data.page === 1 ? items : [...this.data.list, ...items],
            hasMore: items.length === 20,
            loading: false
          })
        }
      })
      .catch(() => this.setData({ loading: false }))
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 })
      this.loadList()
    }
  },

  goEdit() {
    wx.navigateTo({ url: '/pages/journal/edit' })
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    // 简单弹窗显示详情
    const item = this.data.list.find(j => j.id === id)
    if (item) {
      this.setData({ detailItem: item, showDetail: true })
    }
  },

  closeDetail() {
    this.setData({ showDetail: false, detailItem: null })
  },

  deleteEntry(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定删除这条日记吗？',
      success: (res) => {
        if (!res.confirm) return
        const openid = getApp().globalData.openid || wx.getStorageSync('openid')
        request({ url: '/api/journal/' + id, method: 'DELETE', data: { openid } })
          .then(() => {
            const list = this.data.list.filter(j => j.id !== id)
            this.setData({ list, showDetail: false })
            wx.showToast({ title: '已删除' })
          })
          .catch(() => wx.showToast({ title: '删除失败', icon: 'none' }))
      }
    })
  },

  noop() {}
})
