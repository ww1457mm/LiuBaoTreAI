const { request } = require('../../utils/request')

const CAT_MAP = {
  history: '历史文化',
  process: '制作工艺',
  culture: '品鉴文化',
  health: '健康功效',
  brew: '冲泡存储',
  grade: '等级品鉴',
  origin: '产地分布'
}

Page({
  data: {
    list: [],
    category: '',
    // 分类列表：全部 + 各分类
    categories: [
      { key: '', label: '全部' },
      { key: 'history', label: '历史文化' },
      { key: 'process', label: '制作工艺' },
      { key: 'culture', label: '品鉴文化' },
      { key: 'health', label: '健康功效' },
      { key: 'brew', label: '冲泡存储' },
      { key: 'grade', label: '等级品鉴' },
      { key: 'origin', label: '产地分布' }
    ],
    keyword: '',
    loading: true
  },

  onLoad() {
    this.loadList()
  },

  onShow() {
    // 每次页面显示时刷新列表（从详情页返回时可能数据有变化）
    if (!this.data.keyword) {
      this.loadList()
    }
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
    const cat = e.currentTarget.dataset.cat
    const newCat = this.data.category === cat ? '' : cat
    this.setData({ category: newCat, keyword: '', loading: true })
    this.loadList()
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  doSearch() {
    const q = (this.data.keyword || '').trim()
    if (!q) {
      this.setData({ category: '' })
      this.loadList()
      return
    }
    this.setData({ loading: true, category: '' })
    request({ url: '/api/knowledge/search/query', data: { q } })
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

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    if (id) {
      wx.navigateTo({ url: `/pages/knowledge/detail?id=${id}` })
    }
  }
})
