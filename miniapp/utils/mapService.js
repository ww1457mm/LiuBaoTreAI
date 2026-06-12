/**
 * 腾讯地图服务封装
 * 整合 qqmap-wx-jssdk + 路线规划 API
 */

const QQMapWX = require('./qqmap-wx-jssdk')
const { QQMAP_KEY } = require('./config')

const qqmapsdk = new QQMapWX({ key: QQMAP_KEY })

// 路线规划 API 地址
const DIRECTION_URL = 'https://apis.map.qq.com/ws/direction/v1/'

/**
 * 获取用户当前位置（GPS）
 * @returns {Promise<{latitude, longitude}>}
 */
function getUserLocation() {
  return new Promise((resolve, reject) => {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => resolve({ latitude: res.latitude, longitude: res.longitude }),
      fail: (err) => reject(err)
    })
  })
}

/**
 * 地址解析（地址 → 坐标）
 * @param {string} address
 * @returns {Promise<{location, formatted_addresses, address_components}>}
 */
function geocoder(address) {
  return new Promise((resolve, reject) => {
    qqmapsdk.geocoder({
      address,
      success: (res) => resolve(res.result),
      fail: (err) => reject(err)
    })
  })
}

/**
 * 逆地址解析（坐标 → 地址）
 * @param {number} lat
 * @param {number} lng
 * @returns {Promise<{address, formatted_addresses}>}
 */
function reverseGeocoder(lat, lng) {
  return new Promise((resolve, reject) => {
    qqmapsdk.reverseGeocoder({
      location: { latitude: lat, longitude: lng },
      success: (res) => resolve(res.result),
      fail: (err) => reject(err)
    })
  })
}

/**
 * 输入提示（联想搜索）
 * @param {string} keyword
 * @param {string} region 限定城市
 * @returns {Promise<Array>}
 */
function getSuggestion(keyword, region) {
  return new Promise((resolve, reject) => {
    qqmapsdk.getSuggestion({
      keyword,
      region: region || '梧州',
      success: (res) => resolve(res.data || []),
      fail: (err) => reject(err)
    })
  })
}

/**
 * POI 搜索
 * @param {string} keyword
 * @param {object} location 中心点 {latitude, longitude}
 * @param {number} distance 搜索半径（米）
 * @returns {Promise<Array>}
 */
function searchPOI(keyword, location, distance) {
  return new Promise((resolve, reject) => {
    const locationStr = typeof location === 'object'
      ? location.latitude + ',' + location.longitude
      : location
    qqmapsdk.search({
      keyword,
      location: locationStr,
      distance: distance || 5000,
      success: (res) => resolve(res.data || []),
      fail: (err) => reject(err)
    })
  })
}

/**
 * 路线规划（驾车/步行/骑行/公交）
 * @param {object} from 起点 {latitude, longitude}
 * @param {object} to   终点 {latitude, longitude}
 * @param {string} mode driving|walking|bicycling|transit
 * @returns {Promise<{polyline, distance, duration, steps}>}
 */
function planRoute(from, to, mode) {
  mode = mode || 'driving'
  return new Promise((resolve, reject) => {
    const fromStr = from.latitude + ',' + from.longitude
    const toStr = to.latitude + ',' + to.longitude
    wx.request({
      url: DIRECTION_URL + mode + '/',
      data: {
        from: fromStr,
        to: toStr,
        key: QQMAP_KEY
      },
      header: { 'content-type': 'application/json' },
      method: 'GET',
      success(res) {
        const data = res.data
        if (data.status === 0) {
          const result = data.result
          const route = result.routes && result.routes[0]
          if (!route) {
            reject({ message: '未找到路线' })
            return
          }

          // 解析路线坐标点（polyline 是压缩编码的）
          const coors = route.polyline
          const pl = decodePolyline(coors)

          // 提取导航步骤
          const steps = (route.steps || []).map((s, i) => ({
            index: i + 1,
            instruction: s.instruction,
            road_name: s.road_name || '',
            distance: s.distance,
            duration: s.duration
          }))

          resolve({
            polyline: pl,
            distance: route.distance,   // 米
            duration: route.duration,   // 秒
            steps
          })
        } else {
          reject({ message: data.message || '路线规划失败', status: data.status })
        }
      },
      fail(err) {
        reject({ message: '网络请求失败', err })
      }
    })
  })
}

/**
 * 解码腾讯地图压缩编码的 polyline 坐标
 * @param {string|Array<number>} coors 压缩坐标串 或 数字数组
 * @returns {Array<{latitude, longitude}>}
 */
function decodePolyline(coors) {
  // 腾讯地图路线规划返回的是数字数组，不是字符串
  if (Array.isArray(coors)) {
    const points = []
    let index = 0
    const len = coors.length
    let lat = 0
    let lng = 0

    while (index < len) {
      let b, shift = 0, result = 0
      do {
        b = coors[index++]
        result |= (b & 0x1f) << shift
        shift += 5
      } while (b >= 0x20)
      const dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
      lat += dlat

      shift = 0
      result = 0
      do {
        b = coors[index++]
        result |= (b & 0x1f) << shift
        shift += 5
      } while (b >= 0x20)
      const dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
      lng += dlng

      points.push({
        latitude: lat / 1e5,
        longitude: lng / 1e5
      })
    }
    return points
  }

  // 字符串格式（旧版兼容）
  const points = []
  let index = 0
  const len = coors.length
  let lat = 0
  let lng = 0

  while (index < len) {
    let b, shift = 0, result = 0
    do {
      b = coors.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
    lat += dlat

    shift = 0
    result = 0
    do {
      b = coors.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
    lng += dlng

    points.push({
      latitude: lat / 1e5,
      longitude: lng / 1e5
    })
  }
  return points
}

/**
 * 计算两点之间的直线距离（Haversine 公式，单位：米）
 */
function calcDistance(lat1, lng1, lat2, lng2) {
  const R = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

/**
 * 格式化距离
 * @param {number} meters
 * @returns {string}
 */
function formatDistance(meters) {
  if (meters < 1000) return Math.round(meters) + 'm'
  return (meters / 1000).toFixed(1) + 'km'
}

/**
 * 格式化时长
 * @param {number} seconds
 * @returns {string}
 */
function formatDuration(seconds) {
  if (seconds < 60) return '约' + Math.round(seconds) + '秒'
  if (seconds < 3600) return '约' + Math.round(seconds / 60) + '分钟'
  const h = Math.floor(seconds / 3600)
  const m = Math.round((seconds % 3600) / 60)
  return '约' + h + '小时' + (m > 0 ? m + '分钟' : '')
}

module.exports = {
  qqmapsdk,
  getUserLocation,
  geocoder,
  reverseGeocoder,
  getSuggestion,
  searchPOI,
  planRoute,
  decodePolyline,
  calcDistance,
  formatDistance,
  formatDuration
}
