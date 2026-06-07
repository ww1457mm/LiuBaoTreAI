const { request } = require('../../utils/request')

Page({
  data: {
    form: {
      tea_name: '六堡茶',
      tea_type: '熟茶',
      year: 5,
      appearance: '',
      storage: '干仓',
      origin: ''
    },
    storageOptions: ['干仓', '湿仓', '自然存放', '地下室'],
    result: null,
    loading: false,
    showResult: false
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  setYear(e) {
    this.setData({ 'form.year': e.detail.value })
  },

  selectStorage(e) {
    this.setData({ 'form.storage': e.currentTarget.dataset.val })
  },

  submit() {
    if (this.data.loading) return
    this.setData({ loading: true, showResult: false, result: null })
    request({ url: '/api/valuation', method: 'POST', data: this.data.form })
      .then((res) => {
        if (res.code === 0) {
          this.setData({ result: res.data, showResult: true })
        }
        this.setData({ loading: false })
      })
      .catch(() => {
        wx.showToast({ title: '分析失败', icon: 'none' })
        this.setData({ loading: false })
      })
  },

  reset() {
    this.setData({ showResult: false, result: null })
  },

  noop() {}
})
