/**
 * 知识库列表页面 - 展示和搜索六堡茶知识文章
 *
 * 功能说明：
 * 1. 分类筛选：按历史文化、制作工艺等分类浏览
 * 2. 关键词搜索：支持语义搜索（向量检索）
 * 3. 文章列表：展示文章标题、摘要、分类
 * 4. 点击跳转：跳转到文章详情页
 *
 * 数据流：
 * 页面加载 → 请求 API → 获取文章列表 → 渲染页面
 *
 * 依赖：
 * - request: 网络请求工具
 * - 后端 API: GET /api/knowledge, GET /api/knowledge/search/query
 */

const { request } = require('../../utils/request')

/**
 * 分类映射表
 * 将英文分类键转换为中文显示名称
 *
 * 用途：
 * - 后端返回英文分类键（如 "history"）
 * - 前端显示中文名称（如 "历史文化"）
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
   * list: 文章列表，每个文章包含:
   *   - id: 文章 ID
   *   - title: 文章标题
   *   - content: 文章摘要（前 200 字符）
   *   - source: 来源文件路径
   *   - category: 分类（中文）
   *
   * category: 当前选中的分类筛选（英文键）
   * categories: 分类列表（用于渲染筛选标签）
   * keyword: 搜索关键词
   * loading: 是否正在加载
   */
  data: {
    list: [],
    category: '',
    // 分类列表：全部 + 各分类
    categories: [
      { key: '', label: '全部' },
      { key: 'history', label: '历史文化' },
      { key: 'process', label: '制作工艺' },
      { key: 'culture', label: '品鉴文化' },
      { key: 'health', label: '健康功效' },
      { key: 'brew', label: '冲泡存储' },
      { key: 'grade', label: '等级品鉴' },
      { key: 'origin', label: '产地分布' }
    ],
    keyword: '',
    loading: true
  },

  /**
   * 页面加载生命周期
   * 首次进入页面时加载文章列表
   */
  onLoad() {
    this.loadList()
  },

  /**
   * 页面显示生命周期
   * 每次页面显示时刷新列表（从详情页返回时可能数据有变化）
   *
   * 注意：
   * - 如果正在搜索（keyword 不为空），不刷新
   * - 避免覆盖用户的搜索结果
   */
  onShow() {
    if (!this.data.keyword) {
      this.loadList()
    }
  },

  /**
   * 加载文章列表
   *
   * 工作流程：
   * 1. 设置加载状态
   * 2. 构造请求参数（可选的分类筛选）
   * 3. 调用后端 API 获取文章列表
   * 4. 将分类键转换为中文名称
   * 5. 更新页面数据
   * 6. 取消加载状态
   */
  loadList() {
    this.setData({ loading: true })

    // 构造请求参数
    const params = {}
    if (this.data.category) params.category = this.data.category

    // 请求后端 API
    request({ url: '/api/knowledge', data: params })
      .then((res) => {
        if (res.code === 0) {
          // 将分类键转换为中文名称
          const list = (res.data || []).map((item) => ({
            ...item,
            category: CAT_MAP[item.category] || item.category
          }))
          this.setData({ list })
        }
      })
      .finally(() => this.setData({ loading: false }))
  },

  /**
   * 分类筛选点击事件处理
   *
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.cat: 点击的分类键
   *
   * 工作流程：
   * 1. 获取点击的分类键
   * 2. 如果已选中，则取消选中（切换为"全部"）
   * 3. 如果未选中，则选中该分类
   * 4. 清空搜索关键词
   * 5. 重新加载列表
   */
  filterCat(e) {
    const cat = e.currentTarget.dataset.cat
    // 切换选中状态：已选中则取消，未选中则选中
    const newCat = this.data.category === cat ? '' : cat
    this.setData({ category: newCat, keyword: '', loading: true })
    this.loadList()
  },

  /**
   * 搜索输入事件处理
   * @param {Object} e - 事件对象，e.detail.value 为当前输入值
   */
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  /**
   * 执行搜索
   *
   * 工作流程：
   * 1. 获取搜索关键词
   * 2. 如果关键词为空，恢复分类筛选视图
   * 3. 如果有关键词，调用语义搜索 API
   * 4. 将搜索结果的分类转换为中文
   * 5. 更新页面数据
   *
   * 搜索策略：
   * - 优先使用向量语义搜索（后端实现）
   * - 可以搜索语义相近的内容，不仅仅是关键词匹配
   */
  doSearch() {
    const q = (this.data.keyword || '').trim()

    // 关键词为空，恢复默认列表
    if (!q) {
      this.setData({ category: '' })
      this.loadList()
      return
    }

    // 清除分类筛选，执行搜索
    this.setData({ loading: true, category: '' })

    // 调用语义搜索 API
    request({ url: '/api/knowledge/search/query', data: { q } })
      .then((res) => {
        if (res.code === 0) {
          // 将分类键转换为中文名称
          const list = (res.data || []).map((item) => ({
            ...item,
            category: CAT_MAP[item.category] || item.category
          }))
          this.setData({ list })
        }
      })
      .finally(() => this.setData({ loading: false }))
  },

  /**
   * 跳转到文章详情页
   * @param {Object} e - 事件对象
   *   e.currentTarget.dataset.id: 文章 ID
   */
  goDetail(e) {
    const id = e.currentTarget.dataset.id
    if (id) {
      wx.navigateTo({ url: `/pages/knowledge/detail?id=${id}` })
    }
  }
})
