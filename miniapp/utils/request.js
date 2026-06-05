const { BASE_URL } = require('./config')

function request(options) {
  const app = getApp()
  const openid = (app && app.globalData.openid) || wx.getStorageSync('openid') || ''
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'content-type': options.contentType || 'application/json',
        ...options.header
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res.data || { message: '请求失败' })
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function uploadFile(filePath, formData) {
  const { BASE_URL } = require('./config')
  const app = getApp()
  const openid = (app && app.globalData.openid) || wx.getStorageSync('openid') || ''
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: BASE_URL + '/api/recognition',
      filePath,
      name: 'file',
      formData: { openid, ...formData },
      success(res) {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          reject(e)
        }
      },
      fail: reject
    })
  })
}

module.exports = { request, uploadFile, BASE_URL }
