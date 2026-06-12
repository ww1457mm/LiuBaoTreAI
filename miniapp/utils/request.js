const { BASE_URL } = require('./config')

/**
 * 构建 URL：将 data 中的非对象字段拼为 query string（GET/DELETE 等）
 */
function buildUrl(url, method, data) {
  // GET / DELETE 请求把 data 拼到 URL 上
  if (method === 'GET' || method === 'DELETE') {
    if (data && typeof data === 'object') {
      const params = Object.keys(data)
        .filter(k => data[k] !== undefined && data[k] !== null && data[k] !== '')
        .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(data[k]))
      if (params.length > 0) {
        url += (url.includes('?') ? '&' : '?') + params.join('&')
      }
    }
  }
  return url
}

function request(options) {
  const method = (options.method || 'GET').toUpperCase()
  const fullUrl = BASE_URL + buildUrl(options.url, method, options.data)

  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method: method,
      // GET/DELETE: data 已拼到 URL，body 留空
      // POST/PUT: data 放 body
      data: (method === 'GET' || method === 'DELETE') ? {} : (options.data || {}),
      header: {
        'content-type': options.contentType || 'application/json',
        ...options.header
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 后端返回业务错误码（如 401 未登录）
          if (res.data && res.data.code !== undefined && res.data.code !== 0) {
            reject(res.data)
          } else {
            resolve(res.data)
          }
        } else {
          reject({ message: `请求失败 (${res.statusCode})`, statusCode: res.statusCode })
        }
      },
      fail(err) {
        reject({ message: '网络连接失败，请检查网络', err })
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
          if (data.code !== undefined && data.code !== 0) {
            reject(data)
          } else {
            resolve(data)
          }
        } catch (e) {
          reject({ message: '响应解析失败，请检查后端服务', raw: res.data })
        }
      },
      fail(err) {
        reject({ message: '上传失败，请检查网络连接', err })
      }
    })
  })
}

function uploadJournalImage(filePath, openid) {
  const { BASE_URL } = require('./config')

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: BASE_URL + '/api/journal/upload',
      filePath,
      name: 'file',
      formData: { openid },
      success(res) {
        try {
          const data = JSON.parse(res.data)
          if (data.code !== undefined && data.code !== 0) {
            reject(data)
          } else {
            resolve(data)
          }
        } catch (e) {
          reject({ message: '响应解析失败，请检查后端服务', raw: res.data })
        }
      },
      fail(err) {
        reject({ message: '上传失败，请检查网络连接', err })
      }
    })
  })
}

module.exports = { request, uploadFile, uploadJournalImage, BASE_URL }
