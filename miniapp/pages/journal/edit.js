const { request, uploadJournalImage } = require('../../utils/request')

const TEA_TYPES = [
  { key: 'liubao', name: '六堡茶' },
  { key: 'shengpu', name: '生普洱' },
  { key: 'shupu', name: '熟普洱' },
  { key: 'black', name: '红茶' },
  { key: 'green', name: '绿茶' },
  { key: 'white', name: '白茶' },
  { key: 'oolong', name: '乌龙茶' }
]

const FLAVORS = ['花香', '果香', '木质', '药香', '槟榔香', '蜜香', '陈香', '烟香', '菌香', '枣香']

Page({
  data: {
    teaTypes: TEA_TYPES,
    flavors: FLAVORS,
    selectedFlavors: [],
    form: {
      tea_name: '',
      tea_type: 'liubao',
      origin: '',
      brew_temp: '100',
      brew_time: '15',
      tea_amount: '7',
      aroma_score: 3,
      taste_score: 3,
      overall_score: 3,
      notes: ''
    },
    image: '',
    saving: false
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  selectType(e) {
    this.setData({ 'form.tea_type': e.currentTarget.dataset.type })
  },

  setScore(e) {
    const field = e.currentTarget.dataset.field
    const val = e.detail.value
    this.setData({ [`form.${field}`]: val })
  },

  toggleFlavor(e) {
    const flavor = e.currentTarget.dataset.flavor
    let selected = [...this.data.selectedFlavors]
    const idx = selected.indexOf(flavor)
    if (idx >= 0) selected.splice(idx, 1)
    else if (selected.length < 5) selected.push(flavor)
    this.setData({ selectedFlavors: selected })
  },

  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => {
        this.setData({ image: res.tempFiles[0].tempFilePath })
      }
    })
  },

  save() {
    const { form, selectedFlavors, image, saving } = this.data
    if (saving) return
    if (!form.tea_name.trim()) {
      wx.showToast({ title: '请输入茶名', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')

    const doSave = (imageUrl) => {
      request({
        url: '/api/journal',
        method: 'POST',
        data: {
          openid,
          tea_name: form.tea_name,
          tea_type: form.tea_type,
          origin: form.origin,
          brew_temp: form.brew_temp + '°C',
          brew_time: form.brew_time + 's',
          tea_amount: form.tea_amount + 'g/150ml',
          aroma_score: Number(form.aroma_score),
          taste_score: Number(form.taste_score),
          overall_score: Number(form.overall_score),
          flavor_notes: selectedFlavors.join(','),
          notes: form.notes,
          image_url: imageUrl || ''
        }
      }).then((res) => {
        if (res.code === 0) {
          wx.showToast({ title: '记录成功' })
          setTimeout(() => wx.navigateBack(), 1000)
        }
        this.setData({ saving: false })
      }).catch(() => {
        wx.showToast({ title: '保存失败', icon: 'none' })
        this.setData({ saving: false })
      })
    }

    if (image) {
      uploadJournalImage(image, openid).then((res) => {
        doSave(res.image_url || '')
      }).catch((err) => {
        console.error('[日记] 图片上传失败:', err)
        wx.showToast({ title: '图片上传失败，将仅保存文字', icon: 'none' })
        doSave('')
      })
    } else {
      doSave('')
    }
  }
})
