const { request } = require('../../utils/request')

Page({
  data: {
    // 茶知识卡片
    teaFacts: [
      {
        id: 1,
        tag: '历史',
        title: '茶船古道',
        text: '六堡茶沿西江水路运往东南亚，比茶马古道更早连接世界。',
        bg: 'linear-gradient(145deg, #2d5a27, #4a8c3f)'
      },
      {
        id: 2,
        tag: '工艺',
        title: '渥堆的秘密',
        text: '30-50天的渥堆发酵，是六堡茶槟榔香形成的关键。',
        bg: 'linear-gradient(145deg, #8b6914, #c4a574)'
      },
      {
        id: 3,
        tag: '品鉴',
        title: '红浓陈醇',
        text: '四字真言道尽六堡茶精髓——汤色红、滋味浓、香气陈、口感醇。',
        bg: 'linear-gradient(145deg, #5b3a8c, #7b5baa)'
      },
      {
        id: 4,
        tag: '健康',
        title: '越陈越好',
        text: '六堡茶是后发酵茶，存放越久茶性越温和，养胃效果越好。',
        bg: 'linear-gradient(145deg, #1a6b5a, #2d9b8a)'
      }
    ],

    // 快速提问
    questions: [
      { id: 1, q: '六堡茶和普洱茶有什么区别？', hint: '从产地、工艺、口感对比' },
      { id: 2, q: '怎么判断六堡茶的好坏？', hint: '看外形、闻香气、品滋味' },
      { id: 3, q: '六堡茶怎么存放才对？', hint: '干仓、通风、避光、无异味' },
      { id: 4, q: '六堡茶的金花是什么？', hint: '冠突散囊菌，品质好的标志' }
    ],

    // 季节推荐
    season: {},

    // 茶语
    quote: {}
  },

  onLoad() {
    this.setSeason()
    this.setQuote()
  },

  onShow() {
    this.fetchStats()
  },

  // 根据当前季节设置推荐
  setSeason() {
    const month = new Date().getMonth() + 1
    const seasons = [
      { name: '🌸 春', title: '春饮花茶，升发阳气', text: '春天万物复苏，适合喝花茶或新制六堡生茶，帮助散发冬季积郁的寒气，促进阳气升发。', recommend: '三年陈六堡生茶' },
      { name: '☀️ 夏', title: '夏饮绿茶，清热消暑', text: '夏天炎热，六堡茶性温和却不燥热，冷泡六堡别有风味，消暑解渴两不误。', recommend: '冷泡六堡熟茶' },
      { name: '🍂 秋', title: '秋饮乌龙，润燥养阴', text: '秋高气爽，干燥渐起。六堡熟茶汤感醇厚，温润不燥，正适合秋冬过渡。', recommend: '五年陈六堡熟茶' },
      { name: '❄️ 冬', title: '冬饮红茶，温阳暖胃', text: '冬天寒冷，一杯陈年六堡暖身又暖胃。煮着喝更佳，满室茶香。', recommend: '十年陈老六堡' }
    ]
    const idx = month >= 3 && month <= 5 ? 0 : month >= 6 && month <= 8 ? 1 : month >= 9 && month <= 11 ? 2 : 3
    this.setData({ season: seasons[idx] })
  },

  // 茶语
  setQuote() {
    const quotes = [
      { text: '茶之为饮，发乎神农氏，闻于鲁周公。', author: '陆羽《茶经》' },
      { text: '一碗喉吻润，二碗破孤闷。三碗搜枯肠，唯有文字五千卷。', author: '卢仝《七碗茶歌》' },
      { text: '茶烟一缕轻轻扬，搅动兰膏四座香。', author: '李时珍' },
      { text: '人生如茶，沉浮随意；拿起放下，皆是修行。', author: '茶禅一味' }
    ]
    this.setData({ quote: quotes[Math.floor(Math.random() * quotes.length)] })
  },

  fetchStats() {
    const app = getApp()
    const openid = app && app.globalData.openid
    if (!openid) return
    request({ url: '/api/user/profile', data: { openid } })
      .then((data) => {
        if (data) {
          this.setData({
            'stats.recognizeCount': data.recognition_count || 0,
            'stats.qaCount': data.qa_count || 0
          })
        }
      })
      .catch(() => {})
  },

  goChat() { wx.switchTab({ url: '/pages/chat/chat' }) },
  goKnowledge() { wx.navigateTo({ url: '/pages/knowledge/knowledge' }) },
  goBrew() { wx.navigateTo({ url: '/pages/brew/brew' }) },
  goJournal() { wx.navigateTo({ url: '/pages/journal/journal' }) },
  goQuiz() { wx.navigateTo({ url: '/pages/quiz/quiz' }) },
  goValuation() { wx.navigateTo({ url: '/pages/valuation/valuation' }) },
  goRecommend() { wx.navigateTo({ url: '/pages/recommend/recommend' }) },
  goProcess() { wx.navigateTo({ url: '/pages/process/process' }) },
  goHistory() { wx.navigateTo({ url: '/pages/history/history' }) },

  goQuickQuestion(e) {
    const question = e.currentTarget.dataset.q
    const app = getApp()
    app.globalData._pendingQuestion = question
    wx.switchTab({ url: '/pages/chat/chat' })
  }
})
