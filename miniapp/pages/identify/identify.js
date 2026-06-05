const { uploadFile, BASE_URL } = require('../../utils/request')

Page({
  data: {
    task: 'variety',
    imagePath: '',
    result: null,
    loading: false
  },

  switchTask(e) {
    this.setData({ task: e.currentTarget.dataset.task, result: null })
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
    wx.showLoading({ title: '识别中...' })
    uploadFile(path, { task: this.data.task })
      .then((res) => {
        wx.hideLoading()
        if (res.code === 0) {
          const d = res.data
          if (d.image_url && !d.image_url.startsWith('http')) {
            d.full_image_url = BASE_URL + d.image_url
          }
          this.setData({ result: d })
        } else {
          wx.showToast({ title: res.message || '识别失败', icon: 'none' })
        }
      })
      .catch(() => {
        wx.hideLoading()
        wx.showToast({ title: '网络错误，请检查后端', icon: 'none' })
      })
      .finally(() => this.setData({ loading: false }))
  }
})
