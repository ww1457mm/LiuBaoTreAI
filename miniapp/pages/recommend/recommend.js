const { request } = require('../../utils/request')

Page({
  data: {
    step: 0,
    answers: {
      taste: '',
      budget: '',
      purpose: '',
      health: ''
    },
    result: null,
    loading: false,
    showResult: false,
    // 选项
    tasteOptions: [
      { key: 'light', name: '清淡鲜爽', icon: '🌸', desc: '口感柔和，香气清新' },
      { key: 'medium', name: '适中均衡', icon: '🍵', desc: '醇厚协调，层次丰富' },
      { key: 'strong', name: '浓郁醇厚', icon: '🔥', desc: '茶气足，回甘强' }
    ],
    budgetOptions: [
      { key: 'low', name: '50元以下', icon: '💰' },
      { key: 'mid', name: '50-200元', icon: '💰💰' },
      { key: 'high', name: '200-500元', icon: '💰💰💰' },
      { key: 'premium', name: '500元以上', icon: '💎' }
    ],
    purposeOptions: [
      { key: 'daily', name: '日常饮用', icon: '☕' },
      { key: 'collect', name: '收藏投资', icon: '📦' },
      { key: 'gift', name: '送礼', icon: '🎁' }
    ],
    healthOptions: [
      { key: 'lipid', name: '降脂减肥', icon: '🏃' },
      { key: 'stomach', name: '暖胃养胃', icon: '🫶' },
      { key: 'antioxidant', name: '抗氧化', icon: '✨' },
      { key: 'none', name: '无特殊需求', icon: '👍' }
    ]
  },

  selectOption(e) {
    const { step, answers } = this.data
    const key = e.currentTarget.dataset.key
    const fields = ['taste', 'budget', 'purpose', 'health']
    answers[fields[step]] = key
    this.setData({ answers })

    // 自动进入下一步
    if (step < 3) {
      setTimeout(() => this.setData({ step: step + 1 }), 200)
    } else {
      this.submit()
    }
  },

  prevStep() {
    if (this.data.step > 0) {
      this.setData({ step: this.data.step - 1 })
    }
  },

  submit() {
    if (this.data.loading) return
    const { answers } = this.data
    const season = ['春', '夏', '秋', '冬'][Math.floor((new Date().getMonth()) / 3)]

    this.setData({ loading: true })
    request({
      url: '/api/recommend',
      method: 'POST',
      data: { ...answers, season }
    }).then((res) => {
      if (res.code === 0) {
        this.setData({ result: res.data, showResult: true })
      }
      this.setData({ loading: false })
    }).catch(() => {
      wx.showToast({ title: '推荐失败', icon: 'none' })
      this.setData({ loading: false })
    })
  },

  reset() {
    this.setData({
      step: 0,
      answers: { taste: '', budget: '', purpose: '', health: '' },
      result: null,
      showResult: false
    })
  },

  goBack() {
    if (this.data.step > 0) {
      this.setData({ step: this.data.step - 1 })
    } else {
      wx.navigateBack()
    }
  },

  noop() {}
})
