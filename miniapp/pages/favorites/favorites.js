/**
 * 收藏管理页面 - 展示和管理用户的收藏记录
 *
 * 功能说明：
 * 1. 收藏列表：展示所有收藏的记录
 * 2. 类型标签：显示收藏类型（知识/问答/识别）
 * 3. 取消收藏：删除单条收藏记录
 *
 * 数据流：
 * 页面显示 → 请求 API → 获取收藏列表 → 渲染页面
 *
 * 依赖：
 * - request: 网络请求工具
 * - 后端 API: GET /api/favorite, DELETE /api/favorite/{id}
 */

const { request } = require('../../utils/request')

/**
 * 收藏类型映射表
 * 将英文类型键转换为中文显示名称
 *
 * 收藏类型：
 * - knowledge: 知识文章收藏
 * - qa: 问答记录收藏
 * - recognition: 识别记录收藏
 */
const TYPE_MAP = {
  knowledge: '知识',
  qa: '问答',
  recognition: '识别'
}

Page({
  /**
   * 页面数据
   *
   * favorites: 收藏列表，每条收藏包含:
   *   - id: 收藏记录 ID
   *   - fav_type: 收藏类型（英文键）
   *   - typeLabel: 收藏类型（中文）
   *   - target_id: 关联的目标 ID
   *   - title: 收藏标题
   *   - content: 收藏内容
   *   - create_time: 收藏时间
   *
   * loading: 是否正在加载
   */
  data: {
    favorites: [],
    loading: true
  },

  /**
   * 页面显示生命周期
   * 每次页面显示时加载收藏列表
   */
  onShow() {
    this.loadFavorites()
  },

  /**
   * 加载收藏列表
   *
   * 工作流程：
   * 1. 获取用户身份（openid）
   * 2. 验证用户已登录
   * 3. 请求收藏列表 API
   * 4. 将收藏类型键转换为中文名称
   * 5. 更新页面数据
   */
  loadFavorites() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')

    // 用户未登录，清空数据
    if (!openid) {
      this.setData({ loading: false, favorites: [] })
      return
    }

    this.setData({ loading: true })

    // 请求收藏列表 API
    request({ url: '/api/favorite', data: { openid, page: 1, page_size: 100 } })
      .then((res) => {
        if (res.code === 0) {
          // 将收藏类型键转换为中文名称
          const favorites = (res.data || []).map((item) => ({
            ...item,
            typeLabel: TYPE_MAP[item.fav_type] || item.fav_type
          }))
          this.setData({ favorites })
        }
      })
      .catch(() => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
      .finally(() => this.setData({ loading: false }))
  },

  /**
   * 取消收藏
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.id: 收藏记录 ID
   *
   * 工作流程：
   * 1. 弹出确认对话框
   * 2. 用户确认后调用取消收藏 API
   * 3. 从页面数据中移除该收藏
   * 4. 显示取消收藏结果提示
   */
  removeFav(e) {
    const id = e.currentTarget.dataset.id
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')

    // 弹出确认对话框
    wx.showModal({
      title: '提示',
      content: '确定取消收藏吗？',
      success: (res) => {
        if (!res.confirm) return

        // 调用取消收藏 API
        request({
          url: '/api/favorite/' + id,
          method: 'DELETE',
          data: { openid }
        }).then(() => {
          // 从页面数据中移除该收藏
          const favorites = this.data.favorites.filter((f) => f.id !== id)
          this.setData({ favorites })
          wx.showToast({ title: '已取消收藏' })
        }).catch(() => {
          wx.showToast({ title: '删除失败', icon: 'none' })
        })
      }
    })
  }
})
