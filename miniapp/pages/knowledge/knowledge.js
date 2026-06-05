const { request } = require('../../utils/request')

const CAT_MAP = {
  history: '历史文化',
  process: '制作工艺',
  culture: '品鉴文化',
  health: '健康功效'
}

Page({
  data: {
    list: [],
    category: '',
    categories: ['history', 'process', 'culture', 'health'],
    keyword: '',
    loading: true
  },

  onLoad() {
    this.loadList()
  },

  loadList() {
    this.setData({ loading: true })
    const params = {}
    if (this.data.category) params.category = this.data.category
    request({ url: '/api/knowledge', data: params })
      .then((res) => {
        if (res.code === 0) {
          const list = (res.data || []).map((item) => ({
            ...item,
            category: CAT_MAP[item.category] || item.category
          }))
          this.setData({ list })
        }
      })
      .finally(() => this.setData({ loading: false }))
  },

  filterCat(e) {
    this.setData({ category: e.currentTarget.dataset.cat })
    this.loadList()
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  doSearch() {
    const q = (this.data.keyword || '').trim()
    if (!q) {
      this.loadList()
      return
    }
    request({ url: '/api/knowledge/search/query', data: { q } })
      .then((res) => {
        if (res.code === 0) {
          const list = (res.data || []).map((item, i) => ({
            id: i + 1,
            title: item.title,
            content: item.content,
            source: item.source,
            category: CAT_MAP[item.category] || item.category
          }))
          this.setData({ list })
        }
      })
  },

  goDetail(e) {
    wx.navigateTo({ url: `/pages/knowledge/detail?id=${e.currentTarget.dataset.id}` })
  }
})
