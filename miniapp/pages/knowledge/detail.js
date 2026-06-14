/**
 * 知识详情页面 - 显示单篇文章的完整内容
 *
 * 功能说明：
 * 1. 加载文章详情：根据文章 ID 获取完整内容
 * 2. 显示文章信息：标题、分类、来源、完整内容
 * 3. 收藏功能：将文章添加到收藏夹
 *
 * 数据流：
 * 页面加载（带 ID 参数）→ 请求 API → 获取文章详情 → 渲染页面
 *
 * 依赖：
 * - request: 网络请求工具
 * - 后端 API: GET /api/knowledge/{id}
 */

const { request } = require('../../utils/request')

/**
 * 分类映射表
 * 将英文分类键转换为中文显示名称
 */
const CAT_MAP = {
  history: '历史文化',
  process: '制作工艺',
  culture: '品鉴文化',
  health: '健康功效',
  brew: '冲泡存储',
  grade: '等级品鉴',
  origin: '产地分布'
}

Page({
  /**
   * 页面数据
   *
   * article: 文章详情，包含:
   *   - id: 文章 ID
   *   - title: 文章标题
   *   - content: 完整内容
   *   - source: 来源文件路径
   *   - category: 分类（英文键）
   *
   * categoryLabel: 分类中文名称
   * loading: 是否正在加载
   */
  data: {
    article: null,
    categoryLabel: '',
    loading: true
  },

  /**
   * 页面加载生命周期
   *
   * @param {Object} options - 页面参数
   *   options.id: 文章 ID（从列表页跳转时传入）
   *
   * 工作流程：
   * 1. 从页面参数获取文章 ID
   * 2. 设置加载状态
   * 3. 调用后端 API 获取文章详情
   * 4. 将分类键转换为中文名称
   * 5. 更新页面数据
   * 6. 处理错误情况
   */
  onLoad(options) {
    const id = options.id
    this.setData({ loading: true })

    // 请求文章详情 API
    request({ url: `/api/knowledge/${id}` })
      .then((res) => {
        if (res.code === 0) {
          // 请求成功，更新页面数据
          this.setData({
            article: res.data,
            // 将分类键转换为中文
            categoryLabel: CAT_MAP[res.data.category] || res.data.category,
            loading: false
          })
        } else {
          // 文章不存在
          this.setData({ loading: false })
          wx.showToast({ title: '文章不存在', icon: 'none' })
        }
      })
      .catch(() => {
        // 网络错误
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  /**
   * 收藏文章
   *
   * 工作流程：
   * 1. 获取用户身份（openid）
   * 2. 验证文章数据存在
   * 3. 调用收藏 API
   * 4. 显示收藏结果提示
   *
   * 收藏数据：
   * - fav_type: 'knowledge'（知识文章类型）
   * - target_id: 文章 ID
   * - title: 文章标题
   * - content: 文章内容
   */
  addFavorite() {
    const app = getApp()
    const a = this.data.article

    // 验证文章数据
    if (!a || !a.id) return

    // 调用收藏 API
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid: app.globalData.openid,
        fav_type: 'knowledge',  // 收藏类型：知识文章
        target_id: a.id,        // 关联的文章 ID
        title: a.title,         // 收藏标题
        content: a.content      // 收藏内容
      }
    }).then(() => wx.showToast({ title: '收藏成功' }))
      .catch(() => wx.showToast({ title: '收藏失败', icon: 'none' }))
  }
})
