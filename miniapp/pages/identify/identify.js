const { uploadFile, BASE_URL } = require('../../utils/request')

Page({
  data: {
    imagePath: '',
    result: null,
    loading: false
  },

  takePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      success: (res) => this.handleImage(res.tempFiles[0].tempFilePath)
    })
  },

  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: (res) => this.handleImage(res.tempFiles[0].tempFilePath)
    })
  },

  handleImage(path) {
    this.setData({ imagePath: path, result: null })
    this.doRecognize(path)
  },

  doRecognize(path) {
    if (this.data.loading) return
    this.setData({ loading: true })
    uploadFile(path, { task: 'disease' })
      .then((res) => {
        if (res.code === 0) {
          const d = res.data
          if (d.image_url && !d.image_url.startsWith('http')) {
            d.full_image_url = BASE_URL + d.image_url
          }
          const conf = Number(d.confidence) || 0
          d.confidenceText = (conf * 100).toFixed(1) + '%'
          d.confidencePercent = Math.round(conf * 100)
          this.setData({ result: d })
        } else {
          wx.showToast({ title: res.message || '识别失败', icon: 'none' })
        }
      })
      .catch((err) => {
        const msg = err && err.message ? err.message : ''
        if (err && err.code === 401) {
          wx.showModal({
            title: '请先登录',
            content: '识别功能需要登录后才能使用，是否去登录？',
            confirmText: '去登录',
            cancelText: '取消',
            success: (res) => {
              if (res.confirm) wx.navigateTo({ url: '/pages/login/login' })
            }
          })
        } else if (msg.includes('timeout') || msg.includes('网络')) {
          wx.showToast({ title: '网络连接超时，请检查网络', icon: 'none' })
        } else {
          wx.showToast({ title: msg || '请求失败，请检查后端服务', icon: 'none' })
        }
      })
      .finally(() => this.setData({ loading: false }))
  }
})
