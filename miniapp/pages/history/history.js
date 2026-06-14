/**
 * 历史记录页面 - 展示用户的识别记录和问答记录
 *
 * 功能说明：
 * 1. 标签切换：在识别记录和问答记录之间切换
 * 2. 记录列表：展示用户的历史操作记录
 * 3. 收藏问答：将问答记录添加到收藏夹
 * 4. 删除记录：删除单条识别或问答记录
 *
 * 数据流：
 * 页面显示 → 请求 API → 获取历史记录 → 渲染页面
 *
 * 依赖：
 * - request: 网络请求工具
 * - BASE_URL: 服务器基础地址（用于图片 URL 拼接）
 * - 后端 API: GET /api/history, POST /api/favorite, DELETE /api/history/*
 */

const { request, BASE_URL } = require('../../utils/request')

Page({
  /**
   * 页面数据
   *
   * tab: 当前选中的标签（'recognition' 或 'qa'）
   * recognition: 识别记录列表，每条记录包含:
   *   - id: 记录 ID
   *   - image_url: 图片地址
   *   - fullUrl: 完整图片地址（拼接 BASE_URL）
   *   - result: 识别结果
   *   - confidence: 置信度
   *   - description: 描述
   *   - suggestion: 建议
   *   - task_type: 任务类型
   *   - create_time: 创建时间
   *
   * qa: 问答记录列表，每条记录包含:
   *   - id: 记录 ID
   *   - question: 用户问题
   *   - answer: AI 回答
   *   - references: 参考资料列表
   *   - create_time: 创建时间
   *
   * loading: 是否正在加载
   */
  data: {
    tab: 'recognition',
    recognition: [],
    qa: [],
    loading: true
  },

  /**
   * 页面显示生命周期
   * 每次页面显示时加载历史记录
   */
  onShow() {
    this.loadHistory()
  },

  /**
   * 切换标签
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.tab: 要切换的标签名
   */
  switchTab(e) {
    this.setData({ tab: e.currentTarget.dataset.tab })
  },

  /**
   * 加载历史记录
   *
   * 工作流程：
   * 1. 获取用户身份（openid）
   * 2. 验证用户已登录
   * 3. 请求历史记录 API（同时获取识别和问答记录）
   * 4. 处理图片 URL（相对路径拼接 BASE_URL）
   * 5. 更新页面数据
   */
  loadHistory() {
    const app = getApp()
    const openid = app.globalData.openid || wx.getStorageSync('openid')

    // 用户未登录，不加载
    if (!openid) {
      this.setData({ loading: false })
      return
    }

    this.setData({ loading: true })

    // 请求历史记录 API
    // type: 'all' 同时获取识别和问答记录
    request({ url: '/api/history', data: { openid, type: 'all', page: 1, page_size: 50 } })
      .then((res) => {
        if (res.code === 0) {
          // 提取识别记录和问答记录
          const recData = res.data && res.data.recognition
          const qaData = res.data && res.data.qa
          const recItems = recData && recData.items ? recData.items : []
          const qaItems = qaData && qaData.items ? qaData.items : []

          // 处理识别记录：拼接完整的图片 URL
          const recognition = recItems.map((r) => ({
            ...r,
            // 如果是相对路径（以 / 开头），拼接 BASE_URL
            fullUrl: r.image_url && r.image_url.startsWith('/') ? BASE_URL + r.image_url : r.image_url
          }))

          this.setData({ recognition, qa: qaItems, loading: false })
        } else {
          this.setData({ loading: false })
        }
      })
      .catch(() => {
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  /**
   * 收藏问答记录
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.item: 问答记录数据
   *
   * 收藏数据：
   * - fav_type: 'qa'（问答类型）
   * - target_id: 问答记录 ID
   * - title: 用户问题（前 50 字符）
   * - content: AI 回答
   */
  favQa(e) {
    const item = e.currentTarget.dataset.item
    const app = getApp()
    const openid = app.globalData.openid || wx.getStorageSync('openid')

    // 调用收藏 API
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid,
        fav_type: 'qa',
        target_id: item.id,
        title: (item.question || '').slice(0, 50),
        content: item.answer
      }
    }).then(() => {
      wx.showToast({ title: '已收藏' })
    }).catch(() => {
      wx.showToast({ title: '收藏失败', icon: 'none' })
    })
  },

  /**
   * 删除识别记录
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.id: 记录 ID
   *
   * 工作流程：
   * 1. 弹出确认对话框
   * 2. 用户确认后调用删除 API
   * 3. 从页面数据中移除该记录
   * 4. 显示删除结果提示
   */
  deleteRecord(e) {
    const id = e.currentTarget.dataset.id

    // 弹出确认对话框
    wx.showModal({
      title: '提示',
      content: '确定删除此记录吗？',
      success: (res) => {
        if (!res.confirm) return

        const openid = getApp().globalData.openid || wx.getStorageSync('openid')

        // 调用删除 API
        request({
          url: '/api/history/recognition/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          // 从页面数据中移除该记录
          const recognition = this.data.recognition.filter(r => r.id !== id)
          this.setData({ recognition })
          wx.showToast({ title: '已删除' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  },

  /**
   * 删除问答记录
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.id: 记录 ID
   *
   * 工作流程：
   * 1. 弹出确认对话框
   * 2. 用户确认后调用删除 API
   * 3. 从页面数据中移除该记录
   * 4. 显示删除结果提示
   */
  deleteQa(e) {
    const id = e.currentTarget.dataset.id

    // 弹出确认对话框
    wx.showModal({
      title: '提示',
      content: '确定删除此记录吗？',
      success: (res) => {
        if (!res.confirm) return

        const openid = getApp().globalData.openid || wx.getStorageSync('openid')

        // 调用删除 API
        request({
          url: '/api/history/qa/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          // 从页面数据中移除该记录
          const qa = this.data.qa.filter(r => r.id !== id)
          this.setData({ qa })
          wx.showToast({ title: '已删除' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  }
})
