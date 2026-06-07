const { request } = require('../../utils/request')
const mapService = require('../../utils/mapService')

Page({
  data: {
    // 地图状态
    mapCenterLat: 23.48,
    mapCenterLng: 111.18,
    mapScale: 8,
    regions: [],
    markers: [],
    polylines: [],
    loading: true,

    // 用户位置
    userLat: null,
    userLng: null,
    hasLocation: false,

    // 搜索
    searchKeyword: '',
    searchResults: [],
    showSearchResults: false,
    searching: false,

    // 详情弹窗
    selectedRegion: null,
    showDetail: false,

    // 导航
    navigating: false,
    navMode: '', // driving / walking / bicycling
    routeInfo: null, // { distance, duration, steps }
    routeSteps: [],

    // 辅助
    levelLabels: { 1: '核心区', 2: '主产区', 3: '一般产区' },
    levelColors: { 1: '#c0392b', 2: '#e67e22', 3: '#27ae60' }
  },

  onLoad() {
    this.mapCtx = null
    this.loadRegions()
    this.getUserLocation()
  },

  onReady() {
    this.mapCtx = wx.createMapContext('liubaoMap')
  },

  // ==================== 数据加载 ====================

  loadRegions() {
    this.setData({ loading: true })
    request({ url: '/api/regions' })
      .then((res) => {
        if (res.code === 0) {
          const regions = (res.data || []).map(r => ({
            ...r,
            distanceText: ''
          }))
          this.updateMarkers(regions)
          this.setData({ regions, loading: false })
          // 如果已有用户位置，计算距离
          if (this.data.hasLocation) {
            this.calcDistances()
          }
        }
      })
      .catch(() => this.setData({ loading: false }))
  },

  // ==================== 用户定位 ====================

  getUserLocation() {
    mapService.getUserLocation().then((loc) => {
      this.setData({
        userLat: loc.latitude,
        userLng: loc.longitude,
        hasLocation: true
      })
      this.updateMarkers(this.data.regions)
      this.calcDistances()
    }).catch((err) => {
      console.log('获取位置失败:', err)
      wx.showToast({ title: '定位失败，请检查权限', icon: 'none' })
    })
  },

  // 计算用户到各产区的距离
  calcDistances() {
    if (!this.data.hasLocation) return
    const { userLat, userLng, regions } = this.data
    const updated = regions.map(r => {
      const d = mapService.calcDistance(userLat, userLng, r.latitude, r.longitude)
      return { ...r, distanceText: mapService.formatDistance(d) }
    })
    this.setData({ regions: updated })
  },

  // 定位到用户位置
  moveToUser() {
    if (!this.data.hasLocation) {
      this.getUserLocation()
      return
    }
    if (this.mapCtx) {
      this.mapCtx.moveToLocation({
        latitude: this.data.userLat,
        longitude: this.data.userLng,
        scale: 12
      })
    }
  },

  // ==================== 地图标记 ====================

  updateMarkers(regions) {
    const regionMarkers = regions.map((r) => ({
      id: r.id,
      latitude: r.latitude,
      longitude: r.longitude,
      width: 40,
      height: 50,
      callout: {
        content: r.name,
        color: '#fff',
        fontSize: 11,
        borderRadius: 6,
        padding: 5,
        bgColor: this.data.levelColors[r.level] || '#27ae60',
        display: 'BYCLICK'
      }
    }))

    let markers = [...regionMarkers]

    // 添加用户位置标记
    if (this.data.hasLocation) {
      markers.push({
        id: 900001,
        latitude: this.data.userLat,
        longitude: this.data.userLng,
        width: 30,
        height: 30,
        callout: {
          content: '📍 我的位置',
          color: '#333',
          fontSize: 11,
          borderRadius: 6,
          padding: 5,
          bgColor: '#fff',
          display: 'ALWAYS'
        }
      })
    }

    this.setData({ markers })
  },

  // ==================== 搜索功能 ====================

  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ searchKeyword: keyword })
    if (keyword.length < 2) {
      this.setData({ searchResults: [], showSearchResults: false })
      return
    }
    // 输入联想
    mapService.getSuggestion(keyword).then((results) => {
      this.setData({ searchResults: results, showSearchResults: true })
    }).catch(() => {})
  },

  onSearchConfirm() {
    const keyword = this.data.searchKeyword
    if (!keyword) return
    this.setData({ searching: true })

    // 先尝试地理编码
    mapService.geocoder(keyword).then((result) => {
      this.addSearchMarker(result.location, keyword, result.formatted_addresses && result.formatted_addresses.recommend)
      this.setData({ searching: false, showSearchResults: false })
    }).catch(() => {
      // 降级为 POI 搜索
      const loc = this.data.hasLocation
        ? { latitude: this.data.userLat, longitude: this.data.userLng }
        : { latitude: this.data.mapCenterLat, longitude: this.data.mapCenterLng }
      mapService.searchPOI(keyword, loc, 20000).then((results) => {
        if (results.length > 0) {
          const first = results[0]
          this.addSearchMarker(first.location, first.title, first.address)
        } else {
          wx.showToast({ title: '未找到相关地点', icon: 'none' })
        }
        this.setData({ searching: false, showSearchResults: false })
      }).catch(() => {
        this.setData({ searching: false })
        wx.showToast({ title: '搜索失败', icon: 'none' })
      })
    })
  },

  selectSuggestion(e) {
    const item = e.currentTarget.dataset.item
    this.setData({ searchKeyword: item.title, showSearchResults: false })
    this.addSearchMarker(item.location, item.title, item.address)
  },

  addSearchMarker(location, title, address) {
    // 添加搜索结果标记
    const searchMarker = {
      id: Date.now(),
      latitude: location.lat,
      longitude: location.lng,
      width: 36,
      height: 46,
      callout: {
        content: title + (address ? '\n' + address : ''),
        color: '#fff',
        fontSize: 11,
        borderRadius: 6,
        padding: 8,
        bgColor: '#3498db',
        display: 'ALWAYS'
      }
    }

    // 保留产区标记 + 用户标记 + 搜索标记
    const existingMarkers = this.data.markers.filter(m => m.id <= 900000)
    this.setData({
      markers: [...existingMarkers, searchMarker]
    })

    // 移动到搜索结果位置
    if (this.mapCtx) {
      this.mapCtx.moveToLocation({
        latitude: location.lat,
        longitude: location.lng,
        scale: 14
      })
    }
  },

  clearSearch() {
    this.setData({
      searchKeyword: '',
      searchResults: [],
      showSearchResults: false
    })
    // 移除搜索标记
    const markers = this.data.markers.filter(m => m.id <= 900000)
    this.setData({ markers })
  },

  // ==================== 产区选择 ====================

  moveToRegion(region) {
    if (!region) return
    this.setData({
      mapCenterLat: region.latitude,
      mapCenterLng: region.longitude,
      mapScale: 14
    })
    if (this.mapCtx) {
      this.mapCtx.moveToLocation({
        latitude: region.latitude,
        longitude: region.longitude,
        scale: 14
      })
    }
  },

  selectRegion(e) {
    const region = e.currentTarget.dataset.region
    if (!region) return
    this.moveToRegion(region)
    this.setData({ selectedRegion: region, showDetail: true })
  },

  onMarkerTap(e) {
    const markerId = e.detail.markerId
    const region = this.data.regions.find((r) => r.id === markerId)
    if (region) {
      this.moveToRegion(region)
      this.setData({ selectedRegion: region, showDetail: true })
    }
  },

  closeDetail() {
    this.setData({ showDetail: false, selectedRegion: null })
  },

  // ==================== 路线导航 ====================

  startNavigation(e) {
    const mode = e.currentTarget.dataset.mode
    const region = this.data.selectedRegion
    if (!region) return

    if (!this.data.hasLocation) {
      wx.showToast({ title: '请先获取位置', icon: 'none' })
      this.getUserLocation()
      return
    }

    wx.showLoading({ title: '规划路线中...' })

    const from = { latitude: this.data.userLat, longitude: this.data.userLng }
    const to = { latitude: region.latitude, longitude: region.longitude }

    mapService.planRoute(from, to, mode).then((route) => {
      // 绘制路线
      const polyline = [{
        points: route.polyline,
        color: '#2d5a27',
        width: 6,
        arrowLine: true,
        borderColor: '#1e3d1a',
        borderWidth: 2
      }]

      // 构建路线步骤
      const steps = route.steps.map(s => ({
        ...s,
        distanceText: mapService.formatDistance(s.distance),
        durationText: mapService.formatDuration(s.duration)
      }))

      this.setData({
        polylines: polyline,
        navigating: true,
        navMode: mode,
        routeInfo: {
          distance: route.distance,
          duration: route.duration,
          distanceText: mapService.formatDistance(route.distance),
          durationText: mapService.formatDuration(route.duration)
        },
        routeSteps: steps
      })

      // 调整视野以包含整条路线
      if (this.mapCtx && route.polyline.length > 0) {
        this.mapCtx.includePoints({
          points: route.polyline,
          padding: [80, 80, 80, 80]
        })
      }

      wx.hideLoading()
    }).catch((err) => {
      wx.hideLoading()
      wx.showToast({ title: err.message || '路线规划失败', icon: 'none' })
    })
  },

  clearRoute() {
    this.setData({
      polylines: [],
      navigating: false,
      navMode: '',
      routeInfo: null,
      routeSteps: []
    })
    // 恢复视野到选中的产区
    if (this.data.selectedRegion) {
      this.moveToRegion(this.data.selectedRegion)
    }
  },

  switchNavMode(e) {
    const mode = e.currentTarget.dataset.mode
    if (mode === this.data.navMode) return
    // 重新规划
    this.startNavigation({ currentTarget: { dataset: { mode } } })
  },

  // ==================== 其他 ====================

  resetMap() {
    this.setData({
      mapCenterLat: 23.48,
      mapCenterLng: 111.18,
      mapScale: 8
    })
    if (this.mapCtx) {
      this.mapCtx.moveToLocation({
        latitude: 23.48,
        longitude: 111.18,
        scale: 8
      })
    }
  },

  noop() {}
})
