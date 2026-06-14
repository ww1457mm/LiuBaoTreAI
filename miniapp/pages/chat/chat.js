/**
 * 聊天页面逻辑 - AI 问答功能的核心页面
 *
 * 功能说明：
 * 1. 用户输入问题，发送给后端 AI 服务
 * 2. 显示 AI 回答，包含参考资料和推荐主题
 * 3. 支持多轮对话（传入历史记录）
 * 4. 提供快捷问题标签
 * 5. 支持收藏问答记录
 *
 * 数据流：
 * 用户输入 → 发送请求 → 后端 RAG 处理 → 返回回答 → 渲染页面
 *
 * 依赖：
 * - request: 网络请求工具
 * - 后端 API: POST /api/chat
 */

const { request } = require('../../utils/request')

Page({
  /**
   * 页面数据
   *
   * messages: 消息列表，每条消息包含:
   *   - id: 消息唯一标识（时间戳）
   *   - role: 'user' 或 'assistant'
   *   - content: 消息内容
   *   - references: 参考资料列表（仅 AI 消息）
   *   - recommendations: 推荐主题字符串（仅 AI 消息）
   *
   * input: 输入框内容
   * sending: 是否正在等待 AI 回答
   * scrollId: 滚动定位的目标元素 ID
   * quickList: 快捷问题列表
   */
  data: {
    messages: [],
    input: '',
    sending: false,
    scrollId: '',
    quickList: ['六堡茶历史', '冲泡方法', '存储收藏', '健康功效', '制作工艺']
  },

  /**
   * 页面显示时的生命周期函数
   *
   * 功能：
   * - 检查是否有从首页传递的待处理问题
   * - 如果有，自动填入输入框并发送
   *
   * 技术细节：
   * - 微信小程序的 switchTab 不支持 query 参数
   * - 因此使用 globalData 传递数据
   */
  onShow() {
    const app = getApp()
    if (app.globalData._pendingQuestion) {
      const question = app.globalData._pendingQuestion
      app.globalData._pendingQuestion = null
      this.setData({ input: question })
      // 延迟 300ms 发送，确保页面渲染完成
      setTimeout(() => this.send(), 300)
    }
  },

  /**
   * 输入框内容变化事件处理
   * @param {Object} e - 事件对象，e.detail.value 为当前输入值
   */
  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  /**
   * 快捷问题点击事件处理
   * @param {Object} e - 事件对象，e.currentTarget.dataset.q 为问题文本
   *
   * 工作流程：
   * 1. 将快捷问题填入输入框
   * 2. 调用 send() 发送请求
   */
  askQuick(e) {
    this.setData({ input: e.currentTarget.dataset.q })
    this.send()
  },

  /**
   * 发送消息
   *
   * 工作流程：
   * 1. 验证输入内容和发送状态
   * 2. 获取用户 openid（身份标识）
   * 3. 构造用户消息并添加到消息列表
   * 4. 提取对话历史（最近 6 条）
   * 5. 调用后端 API 获取 AI 回答
   * 6. 将 AI 回答添加到消息列表
   * 7. 自动滚动到最新消息
   *
   * 防重复提交：
   * - sending 标志防止重复发送
   * - 请求完成后重置 sending 状态
   */
  send() {
    const question = (this.data.input || '').trim()
    if (!question || this.data.sending) return

    const app = getApp()
    // 获取用户身份标识
    const openid = app.globalData.openid || wx.getStorageSync('openid')

    // 生成消息 ID（使用时间戳）
    const id = Date.now()

    // 构造用户消息
    const userMsg = { id, role: 'user', content: question }

    // 提取对话历史（最近 6 条，即 3 轮对话）
    const history = this.data.messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }))

    // 更新页面状态
    this.setData({
      messages: [...this.data.messages, userMsg],  // 添加用户消息
      input: '',  // 清空输入框
      sending: true,  // 设置发送中状态
      scrollId: `msg-${id}`  // 滚动到用户消息
    })

    // 调用后端 API
    request({
      url: '/api/chat',
      method: 'POST',
      data: { openid, question, history }
    }).then((res) => {
      if (res.code === 0) {
        // 生成 AI 消息 ID
        const aid = Date.now() + 1

        // 构造 AI 消息
        const botMsg = {
          id: aid,
          role: 'assistant',
          content: res.data.answer,
          references: res.data.references || [],
          // 将推荐主题数组转换为字符串
          recommendations: (res.data.recommendations || []).join('、')
        }

        // 更新页面状态
        this.setData({
          messages: [...this.data.messages, botMsg],  // 添加 AI 消息
          scrollId: `msg-${aid}`  // 滚动到 AI 消息
        })
      } else {
        wx.showToast({ title: res.message || '回答失败', icon: 'none' })
      }
    }).catch(() => {
      wx.showToast({ title: '网络错误', icon: 'none' })
    }).finally(() => this.setData({ sending: false }))  // 重置发送状态
  },

  /**
   * 收藏最后一条 AI 回答
   *
   * 工作流程：
   * 1. 获取最后一条消息
   * 2. 验证是否为 AI 回答
   * 3. 调用收藏 API
   * 4. 显示收藏成功提示
   *
   * 收藏数据：
   * - fav_type: 'qa'（问答类型）
   * - title: 用户问题的前 50 个字符
   * - content: AI 回答内容
   */
  onFavoriteLast() {
    const msgs = this.data.messages
    const last = msgs[msgs.length - 1]
    if (!last || last.role !== 'assistant') return

    const app = getApp()
    request({
      url: '/api/favorite',
      method: 'POST',
      data: {
        openid: app.globalData.openid,
        fav_type: 'qa',
        // 使用用户问题作为收藏标题
        title: msgs[msgs.length - 2]?.content?.slice(0, 50) || '问答',
        content: last.content
      }
    }).then(() => wx.showToast({ title: '已收藏' }))
  }
})
